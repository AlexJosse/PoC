from flask import Blueprint, jsonify
from models import process_sql
from config import Config
from services.es_service import create_es_client
from elasticsearch import TransportError

sql_bp = Blueprint('sql_bp', __name__)

@sql_bp.route('/process_sql', methods=['GET'])
def list_sql_files():
    es = create_es_client(Config)
    message = process_sql(Config)
    if "error" in message:
        return jsonify({"error": message}), 500
    patients = message['message']

    return jsonify({"message": patients}), 200
