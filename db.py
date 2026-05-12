import os
from re import I

import psycopg2


def get_connection():
    return psycopg2.connect(host=os.environ.get("DATABASE_HOST"), database = os.environ.get("DATABASE_NAME"), user=os.environ.get("DATABASE_USER"), password = os.environ.get("PASSWORD"))

def user_exists(user):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users WHERE username = %s", [user["username"]])
                count = cur.fetchone()[0]
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cur.close()
            conn.close()
    return count > 0


def login(username, password):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE username = %s AND password = crypt(%s, password)", [username, password])
                user_tuple = cur.fetchone()
                user = None
                if user_tuple is None:
                    return None
                user = {
                    "id": user_tuple[0],
                    "username": user_tuple[1],
                }
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cur.close()
            conn.close()
        return user
