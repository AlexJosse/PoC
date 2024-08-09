# routes/upload.py
import os
import logging
import pysftp
import pandas as pd
from flask import Blueprint, request, jsonify, current_app
from config import Config
from utils.pdf_utils import extract_text_from_pdf, parse_pdf_text
from services.es_service import create_es_client, insert_data_into_elasticsearch
from elasticsearch import Elasticsearch, RequestsHttpConnection, ConnectionError

upload_bp = Blueprint('upload_bp', __name__)

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

es = Elasticsearch(
    [{'host': Config.ES_HOST, 'port': Config.ES_PORT, 'scheme': 'http'}],
    connection_class=RequestsHttpConnection,
    timeout=30,
    max_retries=10,
    retry_on_timeout=True
)

@upload_bp.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('files')

    if not files or files[0].filename == '':
        return jsonify({"error": "No selected file"}), 400

    upload_results = []

    try:
        # Check if Elasticsearch is reachable
        if not es.ping():
            logging.error("Elasticsearch server is not reachable")
            return jsonify({"error": "Elasticsearch server is not reachable"}), 500

        index_name = 'medical_data'
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name)
            logging.debug(f"Created index {index_name} with custom similarity settings")

        for file in files:
            if file:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
                logging.debug(f"Saving file to {file_path}")
                try:
                    file.save(file_path)
                    logging.debug(f"File saved to {file_path}")
                    os.chmod(file_path, 0o777)
                    logging.debug(f"Permissions set for {file_path}")

                    with pysftp.Connection(Config.SFTP_HOST, username=Config.SFTP_USERNAME, password=Config.SFTP_PASSWORD, port=Config.SFTP_PORT, cnopts=cnopts) as sftp:
                        sftp.put(file_path, f'upload/{file.filename}')
                        logging.debug(f"File {file.filename} uploaded to SFTP server")
                    upload_results.append(f"File {file.filename} uploaded successfully")

                    # Process the uploaded file and insert into Elasticsearch
                    if file.filename.endswith('.csv'):
                        data = pd.read_csv(file_path, delimiter=',', quotechar='"', quoting=2)
                        for index, row in data.iterrows():
                            doc = {
                                'PID': row['PID'],
                                'Pathology': row['Pathology'],
                                "from": "csv"
                            }
                            logging.debug(f"Document to index: {doc}")
                            res = es.index(index='medical_data', body=doc)
                            logging.debug(f"Inserted document ID: {res['_id']}")
                    elif file.filename.endswith('.pdf'):
                        text = extract_text_from_pdf(file_path)
                        parsed_data = parse_pdf_text(text)
                        insert_data_into_elasticsearch(es, parsed_data)
                        logging.info(f"Processed and inserted data from {file.filename}")
                    else:
                        logging.error(f"Unsupported file type: {file.filename}")
                        return jsonify({"error": f"Unsupported file type: {file.filename}"}), 400

                except Exception as e:
                    logging.error(f"Error processing file {file.filename}: {str(e)}")
                    return jsonify({"error": str(e)}), 500
                finally:
                    os.remove(file_path)
                    logging.debug(f"File {file.filename} removed from {file_path}")

        return jsonify({"message": "All files uploaded and processed successfully"}), 200

    except ConnectionError as e:
        logging.error(f"Connection error: {str(e)}")
        return jsonify({"error": f"Connection error: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Error processing files: {str(e)}")
        return jsonify({"error": str(e)}), 500
