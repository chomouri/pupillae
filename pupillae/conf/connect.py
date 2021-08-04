#!/usr/bin/python
import psycopg2
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

        # Temp message:
        #cur.execute('SELECT * FROM manufactors')
        #full_list = cur.fetchall()
        #message = f"Test SELECT: {full_list}"

	# close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print("Database connection closed.")
    return

if __name__ == '__main__':
    connect()
