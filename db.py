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

def get_user(user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", [user_id])
                user_tuple = cur.fetchone()
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

def add_user(user):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO users (username, password) VALUES (%s, crypt(%s, gen_salt('bf'))) RETURNING *",  # Encriptado utilizando algoritmo blow fish
                            [user["username"], user["password"]])
                conn.commit()
                user_tuple = cur.fetchone()
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

def get_match(match_id, seq_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                #add new_data validation
                cur.execute("SELECT * FROM match where id = %s AND new_data > %s", [match_id, seq_id])
                match_tuple = cur.fetchone()
                match = None
                if match_tuple is None:
                    return None
                match = {
                        "id": match_tuple[0],
                        "tournament": match_tuple[1],
                        "date_match": match_tuple[2].strftime("%d/%m/%Y"),
                        "player1": match_tuple[3],
                        "player2": match_tuple[4],
                        "isover": match_tuple[5],
                        "winner": match_tuple[6],
                        "users_id": match_tuple[7],
                        "new_data": match_tuple[8],
                        "score": match_tuple[9],
                    }
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cur.close()
            conn.close()
        return match


def get_score(match_id, seq_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT score, new_data, isover, winner FROM match where id = %s AND new_data > %s", [match_id, seq_id])
                match_tuple = cur.fetchone()
                match = None
                if match_tuple is None:
                    return None
                match = {
                        "score": match_tuple[0],
                        "new_data": match_tuple[1],
                        "isover": match_tuple[2],
                        "winner": match_tuple[3],
                    }
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cur.close()
            conn.close()
        return match

def get_all_matchs():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM match order by date_match desc, id desc")
                matchs = []
                for match_tuple in cur.fetchall():
                    match = {
                        "id": match_tuple[0],
                        "tournament": match_tuple[1],
                        "date_match": match_tuple[2].strftime("%d/%m/%Y"),
                        "player1": match_tuple[3],
                        "player2": match_tuple[4],
                        "isover": match_tuple[5],
                        "winner": match_tuple[6],
                        "users_id": match_tuple[7],
                        "new_data": match_tuple[8],
                        "score": match_tuple[9],
                    }
                    matchs.append(match)
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cur.close()
            conn.close()
        return matchs
    

def add_matchs(match, user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO match (tournament, date_match, player1, player2, isover, users_id) VALUES (%s, %s, %s, %s, %s, %s) RETURNING *", [match["tournament"], match["date_match"], match["player1"], match["player2"], 'false', user_id])
                conn.commit()
                match = None
                match = cur.fetchone()
                if match is None:
                    return None

                match = {
                        "id": match[0],
                        "tournament": match[1],
                        "date_match": match[2].strftime("%d/%m/%Y, %H:%M:%S"),
                        "player1": match[3],
                        "player2": match[4],
                        "isover": match[5],
                        "winner": match[6],
                        "users_id": match[7],
                        "new_data": match[8],
                        "score": match[9],
                    }
                return match
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cur.close()
            conn.close()

def remove_match(match_id, user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM score s WHERE match_id in (select m.id from score s, match m where s.match_id = m.id and m.id = %s AND m.users_id = %s)", [match_id, user_id])
                conn.commit()
                cur.execute("DELETE FROM match m WHERE m.id = %s AND m.users_id = %s RETURNING *", [match_id, user_id])
                conn.commit()
                var = None
                var = len(cur.fetchall()) > 0
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cur.close()
            conn.close()
        return var    

def update_match(match_id, match_in, user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE match SET tournament = %s, player1 = %s, player2 = %s, date_match = %s, new_data = new_data + 1 WHERE id = %s AND users_id = %s AND isover = 'false' RETURNING *", [match_in["tournament"], match_in["player1"], match_in["player2"], match_in["date_match"], match_id, user_id])
                conn.commit()
                match = cur.fetchone()
                if match is None:
                    return None
                match = {
                        "id": match[0],
                        "tournament": match[1],
                        "date_match": match[2].strftime("%d/%m/%Y, %H:%M:%S"),
                        "player1": match[3],
                        "player2": match[4],
                        "isover": match[5],
                        "winner": match[6],
                        "users_id": match[7],
                        "new_data": match[8],
                        "score": match[9]
                    }
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cur.close()
            conn.close()
        return match

def update_score(match_id, match_in, user_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT isover from match WHERE id = %s AND isover = 'true' AND users_id = %s", [match_id, user_id])
                conn.commit()
                res = cur.fetchone()
                if res is not None:
                    match = -1
                    return
                cur.execute("UPDATE match SET score = %s, new_data = new_data + 1 WHERE id = %s AND users_id = %s AND isover = 'false' RETURNING *", [match_in["score"], match_id, user_id])
                conn.commit()
                print(type(match_in))
                if "winner" in match_in:
                    cur.execute("UPDATE match SET winner = %s, new_data = new_data + 1 WHERE id = %s AND users_id = %s AND isover = 'false' RETURNING *", [match_in["winner"], match_id, user_id])
                    conn.commit()
                if "isover" in match_in:
                    cur.execute("UPDATE match SET isover = %s, new_data = new_data + 1 WHERE id = %s AND users_id = %s RETURNING *", [match_in["isover"], match_id, user_id])
                    conn.commit()
                match = cur.fetchone()
                if match is None:
                    return None
                match = {
                        "id": match[0],
                        "tournament": match[1],
                        "date_match": match[2].strftime("%d/%m/%Y, %H:%M:%S"),
                        "player1": match[3],
                        "player2": match[4],
                        "isover": match[5],
                        "winner": match[6],
                        "users_id": match[7],
                        "new_data": match[8],
                        "score": match[9]
                    }
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cur.close()
            conn.close()
        return match