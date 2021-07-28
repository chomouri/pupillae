# Connection and Database functions for fons
import psycopg2
from psycopg2 import sql
from conf import config

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

def get_tables(conn):
    table_names = []
    try:
        cur = conn.cursor()
        cur.execute("select relname from pg_class where relkind='r' and relname !~ '^(pg_|sql_)';")
        for table in cur.fetchall():
            table_names.append(table[0])
    except psycopg2.Error as e:
            print(e)
    cur.close()
    return table_names

def get_table_col_names(conn, table_str):
    col_names = []
    query = sql.SQL("SELECT * FROM {table}").format(
        table = sql.Identifier(table_str))
    try:
        cur = conn.cursor()
        cur.execute(query)
        # print(cur.description)
        for desc in cur.description:
            col_names.append(desc[0])
    except psycopg2.Error as e:
        print(e)
    cur.close()
    return col_names

def get_col_details(conn, table_str):
    col_details = []
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT column_name, udt_name, character_maximum_length FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name LIKE {}").format(sql.Literal(table_str)))
        col_details = cur.fetchall()

    except psycopg2.Error as e:
        print(e)
    cur.close()
    return col_details

if __name__ == '__main__':
    fons = connect("fons_pg")
    conn = psycopg2.connect(**fons)

    field="company"
    table='modifactors'

    print(get_col_details(conn, table))


    if conn is not None:
        conn.close()
        print("Database connection closed.")
