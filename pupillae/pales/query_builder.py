# This script uses the table_dict, select_list, order_dict, where_dict from the
# parser to build queries.
#
# Since some of the variables used in building the query are PostgreSQL keywords,
# the scripts in which to build them are in this file.
#
# This script should not be considered to completely santitise the input, instead
# relying on the parser to pass it santitised data, but between the parser and
# query_builder, should be closely guarded as potential avenues for SQL Injections.

# table_dict, select_list, order_dict, where_dict
# ("SELECT * FROM mytable WHERE path LIKE %s ESCAPE ''", (path,))
import psycopg2
from psycopg2 import sql

def build_select(cur, table_dict):
    """ Builds the SELECT statement using the table_dict's "show" values """

    select_list = []
    for column in table_dict.keys():
        if table_dict[column]["show"] == True:
            select_list.append(column)
    if len(select_list) < 1:
        select_list = ["m_name", "squad_name"]
    select_from = sql.SQL(
"""
SELECT
concat_ws('_',
lpad(to_hex(modifactors.m_id), 4, '0'),
lpad(to_hex(modifactors.p_id), 4, '0')) as "Model_ID",
{select}
FROM manufactors
INNER JOIN modifactors ON manufactors.m_id = modifactors.m_id
"""
        ).format(select = sql.SQL(', ').join(map(sql.Identifier, select_list))).as_string(cur)

    return select_from

def build_order(cur, order_dict):
    """ Builds the ORDER BY and LIMIT/OFFSET statement using the
    order_dict's orientation values.

    Notes: It appears that the columns from order_dict do not need to be quoted """

    order_list = []
    if len(order_dict) < 1:
        order_by = 'ORDER BY "Model_ID" ASC'
    else:
        for column, orientation in order_dict.items():
            order_list.append(f"{column} {orientation}")
        order_str = ", ".join(order_list)
        order_str = f"""ORDER BY {order_str}, "Model_ID" ASC"""
        order_by = sql.SQL(order_str).as_string(cur)
    order_by += """
LIMIT %(limit_current)s
OFFSET %(offset_current)s;
"""
    return order_by
