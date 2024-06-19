# routes/csv.py
import os
import logging
import pysftp
import pandas as pd
from flask import Blueprint, jsonify, current_app
from config import Config
from elasticsearch import Elasticsearch

csv_bp = Blueprint('csv_bp', __name__)

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # Disable host key checking

es = Elasticsearch([{'host': Config.ES_HOST, 'port': Config.ES_PORT}])

@csv_bp.route('/process_csv', methods=['GET'])
def process_csv():
    try:
        # Connect to SFTP and download the file
        with pysftp.Connection(Config.SFTP_HOST, username=Config.SFTP_USERNAME, password=Config.SFTP_PASSWORD, port=Config.SFTP_PORT, cnopts=cnopts) as sftp:
            sftp.cwd('upload')
            csv_files = [f for f in sftp.listdir() if f.endswith('.csv')]
            logging.debug(f"File {csv_files}")
            if not csv_files:
                return jsonify({"error": "No CSV files found"}), 400
            sftp.get(csv_files[0], os.path.join(current_app.config['UPLOAD_FOLDER'], csv_files[0]))    

            csv_file = os.path.join(current_app.config['UPLOAD_FOLDER'], csv_files[0])
            logging.debug(f"2) File {csv_file}")
            data = pd.read_csv(csv_file, delimiter=',')

            for index, row in data.iterrows():
                doc = {
                    'PID:': row['PID'],
                    'Pathology': row['Pathology']
                }
                res = es.index(index='medical_data', body=doc)
                logging.debug(f"Inserted document ID: {res['_id']}")

            return jsonify({"message": "Data processed and inserted successfully"}), 200
    
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")
        return jsonify({"error": str(e)}), 500
