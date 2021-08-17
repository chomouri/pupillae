import pales
import parser
from pupillae.conf import connect

queries = [
    "1^m_race=/human/dwarf; 3m_arms=-dagger -hammer; 2m_armor=-shield"
    # , "!m_race=race; material=+metal+bones"
    # , "m_race=human; 2based=True; 3material=+metal+bones+find"
    # , """4painted=3; 3m_arms=-bow+sword+axe-hammer-'great-sword'; 11based=Tru3; 2squad_name=+"Crusher's Raid"; 1!^m_race= -433mm"""
    ]

try:
    conn = connect.connect(user="pales_pg", persist=True)
    cur = conn.cursor()
    for query in queries:
        sql_query, execute_dict = pales.query_db(cur, query)
        print("--->", sql_query)
        print("--->", execute_dict)
        cur.execute(sql_query, execute_dict)
        results = cur.fetchall()
        print(f"\nResults: {results}\n")
except Exception as error:
    print("Error:", error)

finally:
    if conn is not None:
        conn.close()
        print("Database connection closed.")
