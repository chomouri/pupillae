import psycopg2

from pupillae.conf import config


def connect(user: str, persist: bool = False):
    """ Connect to the PostgreSQL database server """
    conn = None
    message = ""
    try:
        # read connection parameters
        params = config.config(section=user)
        user, database = params['user'], params['database']
        message = f"--User:{user} --Database:{database}"

        print(f"Connecting to the PostgreSQL database...\n{message}")
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        print("PostgreSQL database version:")
        cur.execute("SELECT version()")
        db_version = cur.fetchone()
        print(db_version)

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if persist == False:
            if conn is not None:
                conn.close()
                print("Database connection closed.")
    return conn
