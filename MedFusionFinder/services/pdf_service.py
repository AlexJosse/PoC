import os
import logging
import pysftp
from flask import jsonify
from utils.pdf_utils import extract_text_from_pdf, parse_pdf_text
from services.es_service import insert_data_into_elasticsearch
from config import Config  # Import the config module


cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # Disable host key checking

def process_pdf(config, es):
    try:
        with pysftp.Connection(config.SFTP_HOST, username=config.SFTP_USERNAME, password=config.SFTP_PASSWORD, port=config.SFTP_PORT, cnopts=cnopts) as sftp:
            sftp.cwd('upload')
            pdf_files = [f for f in sftp.listdir() if f.endswith('.pdf')]
            if not pdf_files:
                return jsonify({"error": "No PDF files found"}), 400
            sftp.get(pdf_files[0], os.path.join(config.UPLOAD_FOLDER, pdf_files[0]))
            pdf_file = os.path.join(config.UPLOAD_FOLDER, pdf_files[0])
            text = extract_text_from_pdf(pdf_file)
            parsed_data = parse_pdf_text(text)
            insert_data_into_elasticsearch(es, parsed_data)
            return jsonify({"message": "Data processed and inserted successfully"}), 200
    except Exception as e:
        logging.error(f"Error processing PDF: {str(e)}")
        return jsonify({"error": str(e)}), 500
