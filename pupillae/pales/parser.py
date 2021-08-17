from typing import NamedTuple
import re

import query_builder as qb

class Token(NamedTuple):
    type: str
    value: str
    index: int

class PalesError:
    detail: str

def tokenise(code):
    token_specification = [
        ('END',         r';'),                          # Statement terminator
        ('PRIORITY',    r'\d+(?=[^\d;]+=)'),             # Integer or decimal number
        ('COLUMN',      r"'[\w ]+'(?==)|[\w]+(?==)"),   # Word or quoted word
        ('INT',         r'\d+(?=[^\d]+;)'),        # Integer or decimal number
        ('ASSIGN',      r'='),                          # Assignment operator
        ('OP',          r'[\-/!^]'),                # Operators
        ('STRING',      r"""['][\w \-%]+[']|["][\w \-'%]+["]|[\w%]+"""),  # Identifiers
        ('SKIP',        r'[ \t\n\']'),           # Skip over spaces, tabs, calls
        ('MISMATCH',    r'.'),                          # Any other character
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    char_start = 0
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        index = mo.start() - char_start
        if kind == 'PRIORITY':
            value = int(value)
        elif kind == 'INT':
            kind = 'SEARCH'
            value = int(value)
        elif kind == 'STRING':
            kind = 'SEARCH'
        elif kind == 'SKIP':
            continue
        yield Token(kind, value, index)

def build_q_dict(query):
    query_dict = {}
    param_counter = 0
    query_dict[param_counter] = {}
    for token in tokenise(query):
        if token.type == 'MISMATCH':
            error = PalesError()
            error.detail = f"Error: '{token.value}' at position: '{token.index}'"
            return error
        if token.type != 'END':
# Use a [line number][character number] reference structure:
            query_dict[param_counter][f"{token.index}"] = {token.type: token.value}
        else:
            param_counter += 1
            query_dict[param_counter] = {}
    return query_dict

def parse_f_dict(cur, query_dict, table_dict):
    """ Uses the query_dict and table_dict to prepare the find query"""
    error = PalesError()
    where_q = ""
    where_dict = {}
    order_dict = {}
    for param, p_value in query_dict.items():
# Reset default paramters, compile results at end of loop for orderless arguments
        show = False
        orientation = "ASC"
        name = None
        priority = None
        op_andor = "AND "
        op_not = ""
        column_side_complete = False
        for arg, a_value in p_value.items():
            # print("2:", param, p_value, "\n", arg, a_value)
            for k, v in a_value.items():
                print("3:", param, p_value, "\n", arg, a_value, "\n", k, v, "\n")
# Evaluate the conditionals into column-side (SELECT/ORDER) and search-side (WHERE).
                if not column_side_complete:
                    if k == 'COLUMN':
                        name = v
# This conditional helps guard against SQL Injections.
                        if name not in table_dict.keys():
                            error.detail = f"Error: I cannot search the '{name}' column, or it doesn't exist."
                            return error
                    if k == 'PRIORITY':
                        priority = v
                    if v == "!":
                        show = True
                    if v == "^":
                        orientation = "DESC"
                    if v == "/":
                        if param == 0:
                            error.detail = f"Error: The first search cannot be an 'OR' ({v}) search."
                            return error
                        op_andor = "OR "

# After the assignment token has been reached, work on the search-side (WHERE).
                    if v == "=":
                        column_side_complete = True
                        if param == 0:
                            where_statement = f"WHERE {name} "
                        else:
                            where_statement = f"{op_andor}{name} "
                if column_side_complete:
                    if v == "-":
                        op_not = f"NOT "
                    if v == "/":
                        op_andor = f"OR "
                    if k == 'SEARCH':
                        if not where_statement.endswith(f"{name} "):
                            where_statement += f"{op_andor}{name} "
# Assign values to where_dict to be passed during cur.execute()
                        query_index = f"{param}_{arg}"
                        where_dict[query_index] = v
                        where_statement += f"{op_not}LIKE %({query_index})s "

        where_q += where_statement + "\n"

        # Compile arguments for the column (column-side):
        if not name:
            error.detail = f"Error: I need a column to search."
            return error
        if show:
            table_dict[name]["show"] = show
        if orientation:
            table_dict[name]["orientation"] = orientation
        if priority:
            order_dict[name] = priority
        table_dict[name]["query_index"] = param

# Sort the order_dict according to :value priority and re-establish order_dict:
    pre_order = {k: v for k, v in sorted(order_dict.items(), key=lambda item: item[1])}
    order_dict = {}
# Create a dictionary with the orientation of the column as a value
# Orientation is currently using sql.Literal(AsIs()) wrapper.
    for column in pre_order.keys():
        order_dict[column] = f"{table_dict[column]['orientation']}"

    select_q = (qb.build_select(cur, table_dict))
    order_q = (qb.build_order(cur, order_dict))
    sql_query = select_q + where_q + order_q
    return sql_query, where_dict

    # return table_dict, select_list, order_dict, where_dict
