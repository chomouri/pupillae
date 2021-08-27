import os
from typing import Any, List, Optional, Tuple, Dict
import re
import sys

import psycopg2
from psycopg2 import sql

import parser
from pupillae.conf import config

def get_cols() -> Dict[str, Any]:
    """Stand-in function to get database tables/columns.

    For each table, compiles a dictionary of accepted column names and
    assigns a nested dictionary of default values to each column.

    """
    defaults = {"query_index": None, "show": False, "orientation": "ASC"}
    tables = ["manufactors", "modifactors"]
    table_cols = [
        ["material", "company", "m_name"],
        ["based", "painted", "m_class", "m_arms", "m_armor", "m_race", "m_type", "squad_reps", "squad_name"]
        ]
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

def query_db(cur, db_query: str, offset: Optional[Dict[str, int]]):
    """Determine the purpose of query and calls the correct function.

    Parameters
    ----------
    cur :
        The cursor to be used for the query.
    db_query : str
        The message to use for the query. `db_query` uses the following
        syntax and format (by way of indices):
        "FFFF Q...".
        Where:
        "FFFF" is a **four** letter word that is used to call a particular
        function.
        "Q..." is the part that will be passed to the correct function.
    offset : dict, optional
        The offset is a dictionary used in SQL SELECT queries to offset
        searches and limit returns and with the following keys:
        "limit_current": int
        "offset_current": int

    Returns
    -------
    See:
        pales.db_find
        pales.db_show

    Raises
    ------
    TODO: Error implementation.
    ^ Uses return as error string.
    """
    function, params = db_query[:4], db_query[5:]
    print(function, params)
    if function == "find":
        results = db_find(cur, params, offset)
    # elif function == "stat":
    #     results = db_stat(cur, params)
    elif function == "show":
        results =  db_show(cur, params)
    else: results = f"""Malformed query: Needs "$db find " or "$db show"."""
    return results

def db_find(cur, db_query: str, offset_dict: Dict[str, int]) -> str:
    """Build a SQL query and execute that query.

    `db_query` is passed to parser.build_q_dict to be tokenised, then
    passed to parser.parse_f_dict to build a complete query. The query
    is executed and the results are returned.

    Parameters
    ----------
    cur : psycopg cursor
    db_query : str
    offset_dict : dict
        Uses the following keys:
            "limit_current": int
            "offset_current": int

    Raises
    ------
    TODO: Error implementation.
    ^ Uses return as error string.
    """
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

# Update execute_dict with offset_dict values:
            execute_dict.update(offset_dict)
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

def db_show(cur, model_id: str) -> str:
    """Validates Model_ID and returns image path if present.

    Parameters
    ----------
    cur : psycopg cursor
    model_id : str
        XXXX_YYYY format of hex(m_id + p_id)

    Returns
    -------
    str
        Either a string detailing the error,
        or a string of `model_id` and the fully qualified path to the
        .jpg, joined with "||".
        Images are tested for existance, not access.
    """
    model_id = model_id.upper()
    if re.fullmatch(r'[0-9A-F]{4}_[0-9A-F]{4}', model_id):
        img_params = config.config(section="fons_gui")
        photo_dir = img_params["saved_img_dir"]
        image = os.path.join(photo_dir, (model_id + ".JPG"))
        if os.path.isfile(image):
            return f"Model ID: {model_id}||{image}"
        else:
            return f"Cannot find {model_id} photo."
    return f"{model_id} is not a valid Model ID. Use hex values in an XXXX_YYYY format."
