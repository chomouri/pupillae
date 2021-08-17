from itertools import chain
from typing import NamedTuple

import psycopg2
from psycopg2 import sql

import parser


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

def query_db(cur, db_query):
    error = None
    parsed = None
    msg = f"You've searched for {db_query}."

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
        if len(parsed) > 0:
            # table_dict, select_list, order_dict, where_dict = parsed
            # return table_dict, select_list, order_dict, where_dict
            return parsed

# if __name__ == '__main__':
