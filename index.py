import os
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request

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

@app.route('/', methods = ["GET"])
def home():
    return "Welcome to API!"
    
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if "username" not in data or "password" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    user = db.login(data['username'], data["password"])

    if user is None:
        return jsonify({"error": "Check credentials"}), NOT_FOUND_CODE

    token = jwt.encode(
        {'user_id': user['id'], 'exp': datetime.utcnow() + timedelta(minutes=5)}, app.config['SECRET_KEY'], 'HS256')

    user["token"] = token.decode('UTF-8')
    #user["token"] = token
    return jsonify(user), OK_CODE


@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()

    if "username" not in data or "password" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    if (db.user_exists(data)):
        return jsonify({"error": "user already exists"}), BAD_REQUEST_CODE

    user = db.add_user(data)

    return jsonify(user), SUCCESS_CODE



@app.route('/api/meters/readings', methods=['POST'])
def add_readings():
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE
        
        contador_id = data.get('contador_id')
        leitura_kwh = data.get('leitura_kwh')
        
        if contador_id is None or leitura_kwh is None:
            return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE
    
        
        resultado = db.add_reading(contador_id, leitura_kwh, json.dumps(data)) 
        return jsonify(resultado), SUCCESS_CODE

@app.route('/api/admin/anomalies', methods=['GET'])
def get_anomalies():
    
    lista_anomalias = db.get_anomalies()
    
    if not lista_anomalias:
        return jsonify("No anomalies"), OK_CODE
    
    return jsonify(lista_anomalias), OK_CODE

@app.route('/api/market/buy', methods=['POST'])
@app.route('/api/market/match', methods=['POST'])
def ad():
    return 0 
