# Connection and Database functions for fons
from datetime import datetime
from typing import Any, Dict, List
import psycopg2
from psycopg2 import sql
from pupillae.conf import config

def connect(user):
    """ Connect to the PostgreSQL database server """
    conn = None
    message = ""
    try:
        # read connection parameters
        params = config.config(section=user)
        user, database = params['user'], params['database']
        message = f"--User:{user} --Database:{database}"

        # connect to the PostgreSQL server
        print(f"Connecting to the PostgreSQL database...\n{message}")
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

	# execute a statement
        print("PostgreSQL database version:")
        cur.execute("SELECT version()")

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

	# close the communication with the PostgreSQL
        cur.close()
        return params
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return

def get_tables(conn) -> List[str]:
    """Get a list of tables from the database."""
    table_names = []
    try:
        cur = conn.cursor()
        cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
        for table in cur.fetchall():
            table_names.append(table[0])
        cur.close()
    except psycopg2.Error as e:
            print(e)
    return table_names

def get_fk_details(conn) -> dict:
    """Get a dict of primary/foreign keys from the database.

    Returns
    -------
    `fk_dict` : dict
        Forms a dict with the following keys:
            "foreign_table",
            "primary_table",
            "no",
            "fk_column",
            "pk_column",
            "constraint_name"
    """
    fk_dict = {}
    fk_headers = ("foreign_table", "primary_table", "no", "fk_column", "pk_column", "constraint_name")
    try:
        cur = conn.cursor()
    # Query written by Bart Gawrych
        cur.execute(sql.SQL("""select row_number() OVER (),
        kcu.table_name as foreign_table,
        rel_kcu.table_name as primary_table,
        kcu.ordinal_position as no,
        kcu.column_name as fk_column,
        rel_kcu.column_name as pk_column,
        kcu.constraint_name
from information_schema.table_constraints tco
join information_schema.key_column_usage kcu
          on tco.constraint_schema = kcu.constraint_schema
          and tco.constraint_name = kcu.constraint_name
join information_schema.referential_constraints rco
          on tco.constraint_schema = rco.constraint_schema
          and tco.constraint_name = rco.constraint_name
join information_schema.key_column_usage rel_kcu
          on rco.unique_constraint_schema = rel_kcu.constraint_schema
          and rco.unique_constraint_name = rel_kcu.constraint_name
          and kcu.ordinal_position = rel_kcu.ordinal_position
where tco.constraint_type = 'FOREIGN KEY'
order by kcu.table_name,
         kcu.ordinal_position;"""))
        fk_details = cur.fetchall()
        cur.close()
    except psycopg2.Error as e:
        print(e)
    for entry in fk_details:
        row, *details = entry
        row = str(row)
        fk_values = [dict(list(map(tuple, zip(fk_headers, details))))]
        fk_dict.update(zip(row, fk_values))
    return fk_dict

def get_table_col_names(conn, table_str: str) -> List[str]:
    """Get column names from the database."""
    col_names = []
    query = sql.SQL("SELECT * FROM {table}").format(
        table = sql.Identifier(table_str))
    try:
        cur = conn.cursor()
        cur.execute(query)
        for desc in cur.description:
            col_names.append(desc[0])
        cur.close()
    except psycopg2.Error as e:
        print(e)
    return col_names

def get_col_details(conn, table_str: str) -> List[Any]:
    """Get column details from the database.

    Returns
    -------
    `col_details` : List[Any]
        column_name, udt_name, character_maximum_length, column_default
    """
    col_details = []
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT column_name, udt_name, character_maximum_length, column_default FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name LIKE {}").format(sql.Literal(table_str)))
        col_details = cur.fetchall()
        cur.close()
    except psycopg2.Error as e:
        print(e)
    return col_details

def submit_p_sql(conn, query_dict: dict, fk_dict: dict, log_file: str) -> dict:
    """Use `query_dict`, `fk_dict` to compile and insert SQL.

    Returns
    -------
    submitted_p_sql : dict
        key : str
            table name
        value :
            psycopg cursor fetch results

    """
    message = ""
    submitted_p_sql = {}
    base_model_pk = None
    # print("QUERY_DICT:", query_dict)

# Convert empty strings to None, pre-empt PK and FK variables
    for table, column in query_dict.items():
        primary_keys = []
        primary_key_counter = 0
        foreign_keys = []
        for field, value in column.items():
            if value == "(Primary Key)":
# Record Key to delete from query_dict and use in confirm_insert query
                primary_keys.append(field)
                print(f"Primary Key Found in {table}: {primary_keys[0]}")
            if value == "(auto)":
                print(f"Auto Foreign Key Found: Updating to: {base_model_pk}")
                column.update({field : base_model_pk})
                foreign_keys.append(field)
            if value == "":
                column.update({field : None})
# Remove primary key from insert query
        for p_k in primary_keys:
            del column[p_k]
# Form Query
        table_names = list(column.keys())
        table_values = tuple(column.values())
        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING {}").format(
            sql.Identifier(table),
            sql.SQL(', ').join(map(sql.Identifier, table_names)),
            sql.SQL(', ').join(sql.Placeholder() * len(table_names)),
            sql.Identifier(primary_keys[0]))
# Insert query
        try:
            cur = conn.cursor()
            cur.execute(insert_query, table_values)
            returned_pk = cur.fetchone()
            conn.commit()

            if base_model_pk == None:
                base_model_pk = returned_pk
# Fetch SQL Insert
            cur.execute(sql.SQL(
                "SELECT * FROM {} WHERE {} = (%s)"
                    ).format(sql.Identifier(table),
                        sql.Identifier(primary_keys[0])
                        ), returned_pk)
            confirm_insert = cur.fetchone()
            submitted_p_sql[table] = confirm_insert
            log_insert(log_file, table, returned_pk, insert_query.as_string(cur), confirm_insert)
            cur.close()
        except psycopg2.Error as e:
            print(e)
    return submitted_p_sql

def log_insert(log_file, table, pk, query, values):
    """Stand-in logging function."""
    print("Logging insert... (alpha format)")
    with open(log_file, 'a') as f:
        f.write(f"'{table}_{pk}': ['{query}', {list(values)}],\n")

def log_error(psql_query):
    """Stand-in logging function (Not Implemented)."""
    print("Logging errors not implemented...")


#if __name__ == '__main__':
