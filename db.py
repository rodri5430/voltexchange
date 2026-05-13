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

def user_exists(username):
    conn = None
    count = 0 
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM Utilizadores WHERE nome = %s", (username))
            count = cur.fetchone()[0]
    except (Exception, psycopg2.Error) as error:
        print("Erro ao verificar utilizador:", error)
    finally:
        if conn:
            conn.close()
    return count > 0


def login(nome, password):
    conn = None
    user = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Procuramos agora pelo campo Nome
            cur.execute("SELECT UtilizadorID, Nome, PasswordHash FROM Utilizadores WHERE Nome = %s", [nome])
            user_tuple = cur.fetchone()

            if user_tuple:
                user_id, db_nome, hashed_password = user_tuple

                # Verificamos a password
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')): 
                    user = {"id": user_id, "nome": db_nome}
    
    except (Exception, psycopg2.Error) as error:
        return str(error)
    finally:
        if conn: conn.close()
    return user


#https://www.geeksforgeeks.org/python/hashing-passwords-in-python-with-bcrypt/
def add_user(username, passwordText):
    conn = None
    user_id = None
    
    # Hashing (Correto)
    password_bytes = passwordText.encode('utf-8')
    salt = bcrypt.gensalt()
    passwordHashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Utilizadores (Nome, PasswordHash) VALUES (%s, %s) RETURNING UtilizadorID", 
                (username, passwordHashed)
            )
            conn.commit()
            user_id = cur.fetchone()[0]
            # Se chegou aqui, retornamos o ID
            return user_id
            
    except (Exception, psycopg2.Error) as error:
        if conn:
            conn.rollback()
        print(f"Erro na BD: {error}")
        # IMPORTANTE: str(error) transforma o objeto em texto para o Flask não crashar
        return str(error) 
        
    finally:
        if conn is not None:
            conn.close()
def add_reading(contador_id, kwh_valor, dados_audit):
    conn = None
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
            conn.close()
        
    return True

def get_anomalies():
    conn = None
    resultado = []
    
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            query = """
                SELECT LeituraID, ContadorID, DataHora, KWh_Leitura, DadosAudit 
                FROM Leituras 
                WHERE (DadosAudit ? 'temperatura' AND (DadosAudit->>'temperatura')::NUMERIC > 80) OR 
                   (DadosAudit ? 'erro_codigo' AND DadosAudit->>'erro_codigo' IS NOT NULL)
                ORDER BY DataHora DESC
            """
            cur.execute(query)
            resultado = cur.fetchall()
            
    except (Exception, psycopg2.Error) as error:
        return error
        
    finally:
        if conn is not None:
            conn.close()
            
    return resultado

def execute_buy(comprador_id, oferta_id):
    conn = None # Definir fora para o 'finally' e 'except' o reconhecerem
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Chama a Procedure do PostgreSQL
            cur.execute("CALL sp_ExecutarCompraDireta(%s, %s)", (comprador_id, oferta_id))
            conn.commit()
            return False # SUCESSO: Retorna True se o COMMIT funcionar
            
    except (Exception, psycopg2.Error) as error:
        print(f"Erro na compra: {error}")
        if conn:
            conn.rollback()
        return str(error) # ERRO: Retorna a mensagem de erro para o Postman
        
    finally:
        if conn:
            conn.close()

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
            conn.close()
    return False
