import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
import psycopg2
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

@app.route('/login', methods=['POST'])
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


@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()

    if "username" not in data or "password" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    if (db.user_exists(data)):
        return jsonify({"error": "user already exists"}), BAD_REQUEST_CODE

    user = db.add_user(data)

    return jsonify(user), SUCCESS_CODE


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "Authorization" not in request.headers:
            return jsonify({"error": "Token not provided"}), FORBIDDEN_CODE

        token = request.headers['Authorization']
        # Remove Bearer from token
        token = token.split(' ')[1]

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado", "expired": True}), UNAUTHORIZED_CODE
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), FORBIDDEN_CODE

        request.user = db.get_user(data['user_id'])

        return f(*args, **kwargs)

    return decorated


@app.route("/matchs", methods=['POST'])
@auth_required
def add_matchs():
    data = request.get_json()

    if "tournament" not in data or "date_match" not in data or "player1" not in data or "player2" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    matchs = db.add_matchs(data, request.user['id'])

    return jsonify(matchs), SUCCESS_CODE


@app.route('/matchs', methods=['GET'])
@auth_required
def get_matchs():
    matchs = db.get_all_matchs()
    return jsonify(matchs), OK_CODE

@app.route('/match/<int:match_id>', methods=['GET'])
@auth_required
def get_match(match_id):
    seq_id = request.args.get("seq_id") or 1
    match = db.get_match(match_id, seq_id)
    if match is None:
        return jsonify({"error": "No content"}), NO_CONTENT_CODE
    return jsonify(match), OK_CODE

@app.route('/match/<int:match_id>/score', methods=['GET'])
@auth_required
def get_score(match_id):
    seq_id = request.args.get("seq_id") or 1
    match = db.get_score(match_id, seq_id)
    if match is None:
        return jsonify({"error": "No content"}), NO_CONTENT_CODE
    return jsonify(match), OK_CODE

@app.route('/match/<int:match_id>', methods=['DELETE'])
@auth_required
def remove_match(match_id):
    if db.remove_match(match_id, request.user['id']):
        return jsonify({"message": "Match removed with success"}), OK_CODE
    else:
        return jsonify({"error": "Match not found"}), FORBIDDEN_CODE


@app.route('/match/<int:match_id>', methods=['PUT'])
@auth_required
def update_match(match_id):
    data = request.get_json()

    if "tournament" not in data or "player1" not in data or "player2" not in data or "date_match" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    match = db.update_match(match_id, data, request.user['id'])

    if match is None:
        return jsonify({"error": "Match not found"}), NOT_FOUND

    return jsonify(match), OK_CODE


@app.route('/match/<int:match_id>/score', methods=['PUT'])
@auth_required
def update_score(match_id):
    data = request.get_json()

    if "score" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    match = db.update_score(match_id, data, request.user['id'])

    if match is None:
        return jsonify({"error": "match not found"}), NOT_FOUND
    elif match == -1:
        return jsonify({"error": "match is over"}), FORBIDDEN_CODE

    return jsonify(match), OK_CODE

@app.route('/match/<int:match_id>/isover', methods=['PUT'])
@auth_required
def update_match_isOver(match_id):
    data = request.get_json()

    if "winner" not in data:
        return jsonify({"error": "invalid parameters"}), BAD_REQUEST_CODE

    match = db.update_match_isOver(match_id, data, request.user['id'])

    if match is None:
        return jsonify({"error": "Match not found"}), FORBIDDEN_CODE

    return jsonify(match), OK_CODE


if __name__ == "__main__":
    app.run()

