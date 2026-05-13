import os
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request
import jwt
import db

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecretkey')

NOT_FOUND_CODE = 401
OK_CODE = 200
SUCCESS_CODE = 201
NO_CONTENT_CODE = 204
BAD_REQUEST_CODE = 400
UNAUTHORIZED_CODE = 401
FORBIDDEN_CODE = 403
NOT_FOUND = 404
SERVER_ERROR = 500


#PAGINA ENTRADA
@app.route('/', methods = ["GET"])
def home():
    return "Olá Bem-Vindo à VoltExchange!!"
  
  
#LOGIN  
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if "username" not in data or "password" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    user = db.login(data['username'], data["password"])

    if user is None:
        return jsonify({"error": "Check credentials"}), NOT_FOUND_CODE

    token = jwt.encode(
        {'user_id': user['id'], 'exp': datetime.now(timezone.utc)+ timedelta(minutes=5)}, app.config['SECRET_KEY'], 'HS256')

    user["token"] = token
    #user["token"] = token
    return jsonify(user), OK_CODE


#REGISTER
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if "username" not in data or "password" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    if (db.user_exists(data)):
        return jsonify({"error": "user already exists"}), BAD_REQUEST_CODE

    user = db.add_user(data['username'], data['password'])

    return jsonify(user), SUCCESS_CODE




#READINGS
@app.route('/api/meters/readings', methods=['POST'])
def add_readings():
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "missing data"}), NO_CONTENT_CODE
        
        contador_id = data.get('contador_id')
        leitura_kwh = data.get('leitura_kwh')
        
        if contador_id is None or leitura_kwh is None:
            return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE
    
        
        resultado = db.add_reading(contador_id, leitura_kwh, data)
        status_code = SUCCESS_CODE if resultado else BAD_REQUEST_CODE
    
        return jsonify({"success": resultado}), status_code



#ANOMALIES
@app.route('/api/admin/anomalies', methods=['GET'])
def get_anomalies():
    
    lista_anomalias = db.get_anomalies()
    
    if not lista_anomalias:
        return jsonify([]), NOT_FOUND_CODE
    
    return jsonify(lista_anomalias), OK_CODE



#BUY
@app.route('/api/market/buy', methods=['POST'])
def buy():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "missing data"}), NO_CONTENT_CODE
    
    utilizador_id = data.get('utilizador_id')
    oferta_id = data.get('oferta_id')
    
    if not utilizador_id or not oferta_id:
        return jsonify({"error": "Incomplete purchase details"}), BAD_REQUEST_CODE
    
    deu_erro = db.execute_buy(utilizador_id, oferta_id)
    
    if deu_erro:
        return jsonify({"error": "Purchase Error"}), BAD_REQUEST_CODE
    
    return jsonify({"message": "Purchase Done!", "detalhes": f"A oferta {oferta_id} foi adquirida pelo utilizador {utilizador_id}."}), SUCCESS_CODE


#ORDER
@app.route('/api/market/order', methods=['POST'])
def order():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "missing data"}), NO_CONTENT_CODE
    
    comprador_id = data.get('utilizador_id')
    quantidade = data.get('quantidade')
    preco_max = data.get('preco_maximo')
    
    if not all([comprador_id, quantidade, preco_max]):
        return jsonify({"error": "incomplete parameters"}), BAD_REQUEST_CODE
    
    deu_erro = db.execute_create_order(comprador_id, quantidade, preco_max)
    
    if deu_erro:
        return jsonify({"error": deu_erro}), BAD_REQUEST_CODE
    
    return jsonify({"message": "Ordem de compra registada!", "detalhes": f"Procura de {quantidade} kWh até {preco_max}€/kWh."}), SUCCESS_CODE   


#MATCH
@app.route('/api/market/match', methods=['POST'])
def match():
    deu_erro = db.execute_matching_engine()
    
    if deu_erro:
        return jsonify({"error": deu_erro}), BAD_REQUEST_CODE
    
    return jsonify({"message": "Motor de matching executado com sucesso!", "detalhes": "As ordens compatíveis foram processadas e as transações geradas."}), SUCCESS_CODE
