import os
import re
import sys

import psycopg2
from psycopg2 import sql

import parser
from pupillae.conf import config

def get_cols():
    """ Stand-in function to get database tables/columns """

    defaults = {"query_index": None, "show": False, "orientation": "ASC"}
    tables = ["manufactors", "modifactors"]
    table_cols = [["material", "company", "m_name"],
        ["based", "painted", "m_class", "m_arms", "m_armor", "m_race", "m_type", "squad_reps", "squad_name"]]
    table_dict = {}

# Build column dictionaries with default values.
    for columns in table_cols:
        table_dict.update(dict.fromkeys(columns, defaults))
# Note table name for each column.
    for i, cols in enumerate(table_cols):
        for col in cols:
            table_dict[col] = {"table": tables[i]} # Yeah... well
            table_dict[col].update(defaults)
    return table_dict

def query_db(cur, db_query: str) -> str:
    """ Determine the purpose of the query and calls the correct function """
    function, params = db_query[:4], db_query[5:]
    print(function, params)
    if function == "find":
        results = db_find(cur, params)
    # elif function == "stat":
    #     results = db_stat(cur, params)
    elif function == "show":
        results =  db_show(cur, params)
    else: results = f"""Malformed query: Needs "$db find "."""
    return results

def db_find(cur, db_query):
    """ Build a SQL query by sending the parameters to the appropriate function """
    error = None
    parsed = None
    msg = f"Searching for: {db_query}"

    table_dict = get_cols()
    query_dict = parser.build_q_dict(db_query)

    if type(query_dict) ==  parser.PalesError:
        error = query_dict.detail
        return error
    else:
        parsed = parser.parse_f_dict(cur, query_dict, table_dict)
        if type(parsed) == parser.PalesError:
            error = parsed.detail
            return error
        if len(parsed) > 1:
            sql_query, execute_dict = parsed
            print("--->", sql_query)
            print("--->", execute_dict)
            try:
                cur.execute(sql_query, execute_dict)
                results = cur.fetchall()
                msg = ""
                for entry in results:
                    msg += str(entry) + "\n"
            except Exception as error:
                return error
            return msg

def db_show(cur, model_id):
    """ Return the full path of image requested and santitises request """
    model_id = model_id.upper()
    if re.fullmatch(r'[0-9A-F]{4}_[0-9A-F]{4}', model_id):
        img_params = config.config(section="fons_gui")
        photo_dir = img_params["saved_img_dir"]
        image = os.path.join(photo_dir, (model_id + ".JPG"))
        print(image)
        if os.path.isfile(image):
            return f"Model ID: {model_id}||{image}"
        else:
            return f"Cannot find {model_id} photo"
    return f"{model_id} is not a valid Model ID. Use hex values in an XXXX_YYYY format."
