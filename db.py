import json
import os
import bcrypt
import psycopg2
from re import I

import psycopg2


def get_connection():
  return psycopg2.connect(
        host="aid.estgoh.ipc.pt", 
        database="db2024153215", 
        user="a2024153215", 
        password="RumoAo20",
    )

def user_exists(user):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users WHERE username = %s", [user["username"]])
                count = cur.fetchone()[0]
    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if conn :
            cur.close()
            conn.close()
    return count > 0


def login(username, password):
    user = None
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Procuramos o utilizador apenas pelo username
                # Importante: mudei para "Utilizadores" para ser igual ao add_user
                cur.execute("SELECT UtilizadorID, username, password FROM Utilizadores WHERE username = %s", [username])
                user_tuple = cur.fetchone()

                if user_tuple:
                    user_id = user_tuple[0]
                    db_username = user_tuple[1]
                    hashed_password = user_tuple[2]

                    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')): 
                        user = {"id": user_id, "username": db_username }
                        
    except (Exception, psycopg2.Error) as error :
        print (error)
        return None
    finally:
        if conn:
            cur.close()
            conn.close()
    return user


#https://www.geeksforgeeks.org/python/hashing-passwords-in-python-with-bcrypt/
def add_user(username, passwordText):
    
    bytes = passwordText.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    passwordHashed = hash.decode('utf-8')
    
    try:
        
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO Utilizadores (username, password) VALUES (%s, %s) RETURNING UtilizadorID", (username, passwordHashed))
                conn.commit()
                id = cur.fetchone()[0]
    except (Exception, psycopg2.Error) as error:
        if conn:
            conn.rollback()
        print(error)
        return None
    finally:
        if conn:
            cur.close()
            conn.close()
    return id
    
def add_reading(contador_id, kwh_valor, dados_audit):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO Leituras (ContadorID, DataHora, KWh_Leitura, DadosAudit)  VALUES (%s, CURRENT_TIMESTAMP, %s, %s)", (contador_id, kwh_valor, json.dumps(dados_audit)))
                conn.commit()
            
    except (Exception, psycopg2.Error) as error:
        print(error)
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            cur.close()
            conn.close()
        
    return True

def get_anomalies():
    resultado = []
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT LeituraID, ContadorID, DataHora, KWh_Leitura, DadosAudit FROM Leituras WHERE KWh_Leitura < 0 OR KWh_Leitura > 500 ORDER BY DataHora DESC")
                
                resultado = cur.fetchall()
    except (Exception, psycopg2.Error) as error:
        return "Error on fetching anomalies!"
        print(error)
    finally:
        if conn:
            cur.close()
            conn.close()
            
    return resultado

def execute_buy(comprador_id, oferta_id):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL sp_ExecutarCompraDireta(%s, %s)", (comprador_id, oferta_id))
                conn.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        if conn:
            conn.rollback()
        
        return True
    finally:
        if conn:
            cur.close()
            conn.close()
    return False

def execute_create_order(comprador_id, quantidade, preco_max):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
            
                cur.execute("INSERT INTO OrdensCompra (CompradorID, QuantidadeKWh, PrecoMaximo, Estado) VALUES (%s, %s, %s, 'PENDENTE')", (comprador_id, quantidade, preco_max))
                
                conn.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        if conn:
            conn.rollback()
        return True
    finally:
        if conn:
            cur.close()
            conn.close()

    return False

def execute_matching_engine():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL sp_MatchingEngine()")
                conn.commit()
    except (Exception, psycopg2.Error) as error:
        print(error)
        
        if conn:
            conn.rollback()
            
        return True
    finally:
        if conn:
            cur.close()
            conn.close()
    return False
