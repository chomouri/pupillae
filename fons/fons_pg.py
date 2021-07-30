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
        cur.close()
    except psycopg2.Error as e:
            print(e)
    return table_names

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
        cur.close()
    except psycopg2.Error as e:
        print(e)
    for entry in fk_details:
        row, *details = entry
        row = str(row)
        fk_values = [dict(list(map(tuple, zip(fk_headers, details))))]
        fk_dict.update(zip(row, fk_values))
    return fk_dict

def get_table_col_names(conn, table_str):
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

def get_col_details(conn, table_str):
    col_details = []
    try:
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT column_name, udt_name, character_maximum_length, column_default FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name LIKE {}").format(sql.Literal(table_str)))
        col_details = cur.fetchall()
        cur.close()
    except psycopg2.Error as e:
        print(e)
    return col_details

def submit_p_sql(conn, query_dict, fk_dict):
    # Convert empty strings to None
    for table, column in query_dict.items():
        primary_keys = []
        primary_key_counter = 0
        foreign_keys = []
        for field, value in column.items():
            if value == "(Primary Key)":
                # Record Key to delete from Insert Query
                primary_keys.append(field)
            if value == "(auto)":
                print("F-Key Found")
                column.update({field : None})# INSERT FK IN NEXT CODE BLOCK
                foreign_keys.append(field)
            if value == "":
                column.update({field : None})
        for p_k in primary_keys:
            del column[p_k]
        table_names = list(column.keys())
        table_values = tuple(column.values())
        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING {}").format(
            sql.Identifier(table),
            sql.SQL(', ').join(map(sql.Identifier, table_names)),
            sql.SQL(', ').join(sql.Placeholder() * len(table_names)),
            # Use p_k instead of doing it properly with fk_dict
            sql.Identifier(p_k))
        print("Note Key ^^^")

        try:
            cur = conn.cursor()
            cur.execute(insert_query, table_values)
            conn.commit()
            print(cur.fetchall())
            cur.close()
        except psycopg2.Error as e:
            print(e)

    # print("COMPOSING...", query_dict)
    # print(fk_dict)
    for constraint, details in fk_dict.items():
        for description, value in details.items():
            # psuedo code:
            """
            SELECT fk_dict[constraint]['pk_column']
              FROM fk_dict[constraint]['primary_table']
            Use Latest or Previously Executed Cursor = saved_FK_value
            INSERT INTO fk_dict[constraint]['foreign_table']
              (fk_dict[constraint]['fk_column']) VALUES saved_FK_value
            """
        print(f"TODO: Update foreign_table: {fk_dict[constraint]['foreign_table']}")

    # connection.commit()
    message = "SUCCESS-- kinda"
    return message




if __name__ == '__main__':
    fons = connect("fons_pg")
    conn = psycopg2.connect(**fons)

    query_dict = {'manufactors': {'m_id': '(Primary Key)', 'code': None, 'material': "METAL", 'company': "CITADEL", 'model_range': "WFB", 'company': "ffdrh", 'year_prod': "DWARF", 'm_name': None}, 'modifactors': {'p_id': '(Primary Key)', 'm_id': "(auto)", 'base': None, 'based': False, 'painted': 4, 'modded': False, 'artist': "ME", 'p_name': None, 'p_location': None, 'photo': "/HOME/PHOTO.JPG", 'm_class': None, 'm_arms': "SWORD", 'm_armor': "LEATHER", 'm_race': "HUMAN", 'm_type': None}}


    fk_dict = get_fk_details(conn)

    try:
        fons = connect("fons_pg")
        conn = psycopg2.connect(**fons)
        submit_p_sql(conn, query_dict, fk_dict)
    except psycopg2.Error as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")
