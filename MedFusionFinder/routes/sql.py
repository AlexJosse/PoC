from flask import Blueprint, jsonify
from models import process_sql
from config import Config
from services.es_service import create_es_client, insert_data_into_es_sql
from elasticsearch import TransportError

sql_bp = Blueprint('sql_bp', __name__)

@sql_bp.route('/process_sql', methods=['GET'])
def list_sql_files():
    es = create_es_client(Config)
    message = process_sql(Config)
    if isinstance(message, str) and "error" in message:
        return jsonify({"error": message}), 500
    if isinstance(message, list):
        patients = message
    else:
        return jsonify({"error": "Unexpected response format from process_sql"}), 500
    message = insert_data_into_es_sql(es, patients)
    if "error" in message:
        return jsonify({"error": message}), 500
    return jsonify({"message": patients}), 200

