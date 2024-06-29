# routes/csv.py
import os
import logging
import pysftp
import pandas as pd
from flask import Blueprint, jsonify, current_app
from config import Config
from elasticsearch import Elasticsearch, RequestsHttpConnection, ConnectionError

csv_bp = Blueprint('csv_bp', __name__)

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # Disable host key checking

es = Elasticsearch(
    [{'host': Config.ES_HOST, 'port': Config.ES_PORT, 'scheme': 'http'}],
    connection_class=RequestsHttpConnection,
    timeout=30,  # Increase the timeout to 30 seconds
    max_retries=10,
    retry_on_timeout=True
)

@csv_bp.route('/process_csv', methods=['GET'])
def process_csv():
    try:
        # Check if Elasticsearch is reachable
        if not es.ping():
            logging.error("Elasticsearch server is not reachable")
            return jsonify({"error": "Elasticsearch server is not reachable"}), 500

        similarity_settings = {
            "similarity": {
                "default": {
                    "type": "BM25",
                    "k1": 1.5,
                    "b": 0.75
                }
            }
        }

        index_name = 'medical_data'
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name, body={"settings": similarity_settings})
            logging.debug(f"Created index {index_name} with custom similarity settings")
        else:
            es.indices.put_settings(index=index_name, body={"settings": similarity_settings})
            logging.debug(f"Updated index {index_name} with custom similarity settings")

        # Connect to SFTP and download the files
        with pysftp.Connection(Config.SFTP_HOST, username=Config.SFTP_USERNAME, password=Config.SFTP_PASSWORD, port=Config.SFTP_PORT, cnopts=cnopts) as sftp:
            sftp.cwd('upload')
            csv_files = [f for f in sftp.listdir() if f.endswith('.csv')]
            logging.debug(f"CSV files: {csv_files}")
            if not csv_files:
                return jsonify({"error": "No CSV files found"}), 400

            for csv_file_name in csv_files:
                local_csv_path = os.path.join(current_app.config['UPLOAD_FOLDER'], csv_file_name)
                sftp.get(csv_file_name, local_csv_path)
                logging.debug(f"Downloaded {csv_file_name} to {local_csv_path}")

                data = pd.read_csv(local_csv_path, delimiter=',')
                for index, row in data.iterrows():
                    doc = {
                        'PID': row['PID'],
                        'Pathology': row['Pathology']
                    }
                    logging.debug(f"Document to index: {doc}")
                    res = es.index(index='medical_data', body=doc)
                    logging.debug(f"Inserted document ID: {res['_id']}")

            return jsonify({"message": "All CSV files processed and inserted successfully"}), 200

    except ConnectionError as e:
        logging.error(f"Connection error: {str(e)}")
        return jsonify({"error": f"Connection error: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")
        return jsonify({"error": str(e)}), 500
