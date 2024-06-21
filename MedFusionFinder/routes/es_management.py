# routes/es_management.py
from flask import Blueprint, jsonify
from services.es_service import create_es_client, clean_elasticsearch_index
from config import Config

es_management_bp = Blueprint('es_management_bp', __name__)

@es_management_bp.route('/clean_index', methods=['GET'])
def clean_index():
    es = create_es_client(Config)
    result = clean_elasticsearch_index(es)
    return jsonify(result), 200
