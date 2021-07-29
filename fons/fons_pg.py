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
        cur.execute(sql.SQL("SELECT column_name, udt_name, character_maximum_length, column_default FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name LIKE {}").format(sql.Literal(table_str)))
        col_details = cur.fetchall()

    except psycopg2.Error as e:
        print(e)
    cur.close()
    return col_details

def get_fk_details(conn):
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

    except psycopg2.Error as e:
        print(e)
    cur.close()
    # for entry in fk_details:
    #     row, *details = entry
    #     print(row, details)
    #     fk_dict.update(row, zip(fk_headers, fk_details))
    #     col_values = [dict(list(map(tuple, zip(col_keys, detail))))]
    #     table_values.update(zip(col_name, col_values))
    for entry in fk_details:
        row, *details = entry
        fk_values = [dict(list(map(tuple, zip(fk_headers, details))))]
        fk_dict.update(zip(str(row), fk_values))
    return fk_dict

def compose_psql(query_dict):
    print("COMPOSING...", query_dict)
    message = "SUCCESS"
    return message

if __name__ == '__main__':
    fons = connect("fons_pg")
    conn = psycopg2.connect(**fons)

    field="company"
    table='modifactors'

    print(get_fk_details(conn))


    if conn is not None:
        conn.close()
        print("Database connection closed.")
