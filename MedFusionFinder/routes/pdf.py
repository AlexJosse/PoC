# routes/pdf.py
from flask import Blueprint, jsonify
from config import Config
from services.pdf_service import process_service_pdf
from services.es_service import create_es_client

pdf_bp = Blueprint('pdf_bp', __name__)

@pdf_bp.route('/process_pdf', methods=['GET'])
def process_pdf():
    es = create_es_client(Config)
    result = process_service_pdf(Config, es)
    status_code = result.pop('status_code')  # Extract the status code from the result dictionary
    return jsonify(result), status_code
