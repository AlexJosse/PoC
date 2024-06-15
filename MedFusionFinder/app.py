from flask import Flask, jsonify, request, render_template
import mysql.connector
from mysql.connector import Error
import pysftp
from faker import Faker
import pandas as pd
import fitz
import re
from elasticsearch import Elasticsearch, TransportError
import os
import sys
import logging

app = Flask(__name__)

# MySQL and Elasticsearch details
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3356))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
MYSQL_DB = os.getenv('MYSQL_DB', 'hospital')
ES_HOST = os.getenv('ES_HOST', 'elasticsearch1')
ES_PORT = int(os.getenv('ES_PORT', 9200))
ES_INDEX = os.getenv('ES_INDEX', 'medical_data')


# SFTP details
SFTP_HOST = os.getenv('SFTP_HOST', 'sftp')
SFTP_PORT = int(os.getenv('SFTP_PORT', 22))
SFTP_USERNAME = os.getenv('SFTP_USERNAME', 'sftpuser')
SFTP_PASSWORD = os.getenv('SFTP_PASSWORD', 'password')

# Initialize Elasticsearch client
es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT}])


# Disable host key checking for testing
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # Disable host key checking

UPLOAD_FOLDER = '/app/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def create_connection_to_db():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

@app.route('/create_database', methods=['GET'])
def create_database():
    connection = create_connection_to_db()
    query = f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}"
    cursor = connection.cursor()
    try:
        response = cursor.execute(query)
        connection.commit()
        return jsonify({"message": f"Database {MYSQL_DB} created successfully, {response}"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test_sftp_connection', methods=['GET'])
def test_sftp_connection():
    try:
        with pysftp.Connection(SFTP_HOST, username=SFTP_USERNAME, password=SFTP_PASSWORD, port=SFTP_PORT, cnopts=cnopts) as sftp:
            sftp.listdir('.')
            return jsonify({"message": "Connection to SFTP server successful"}), 200
    except Exception as e:
        logging.error(f"Error testing SFTP connection: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('files')

    if not files or files[0].filename == '':
        return jsonify({"error": "No selected file"}), 400

    upload_results = []

    for file in files:
        if file:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            logging.debug(f"Saving file to {file_path}")
            try:
                file.save(file_path)
                logging.debug(f"File saved to {file_path}")
                os.chmod(file_path, 0o777)
                logging.debug(f"Permissions set for {file_path}")

                with pysftp.Connection(SFTP_HOST, username=SFTP_USERNAME, password=SFTP_PASSWORD, port=SFTP_PORT, cnopts=cnopts) as sftp:
                    sftp.put(file_path, f'upload/{file.filename}')
                    logging.debug(f"File {file.filename} uploaded to SFTP server")
                upload_results.append(f"File {file.filename} uploaded successfully")
            except Exception as e:
                logging.error(f"Error saving file {file.filename}: {str(e)}")
                return jsonify({"error": str(e)}), 500
            finally:
                os.remove(file_path)
                logging.debug(f"File {file.filename} removed from {file_path}")

    return jsonify({"message": upload_results}), 200

@app.route('/list_files', methods=['GET'])
def list_files():
    try:
        with pysftp.Connection(SFTP_HOST, username=SFTP_USERNAME, password=SFTP_PASSWORD, port=SFTP_PORT, cnopts=cnopts) as sftp:
            sftp.cwd('upload')
            files = sftp.listdir()
        return jsonify({"files": files}), 200
    except Exception as e:
        logging.error(f"Error listing files: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/process_csv', methods=['GET'])
def process_csv():
    try:
        # Connect to SFTP and download the file
        with pysftp.Connection(SFTP_HOST, username=SFTP_USERNAME, password=SFTP_PASSWORD, port=SFTP_PORT, cnopts=cnopts) as sftp:
            sftp.cwd('upload')
            csv_files = [f for f in sftp.listdir() if f.endswith('.csv')]
            logging.debug(f"File {csv_files}")
            if not csv_files:
                return jsonify({"error": "No CSV files found"}), 400
            sftp.get(csv_files[0], os.path.join(app.config['UPLOAD_FOLDER'], csv_files[0]))    

            csv_file = os.path.join(app.config['UPLOAD_FOLDER'], csv_files[0])
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

def extract_text_from_pdf(file_path):
    document = fitz.open(file_path)
    text = ""
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def parse_pdf_text(text):
    # Define regex patterns for the fields
    patterns = {
        "Indication": r"Indication\s*([\s\S]*?)(?=Technique|Description|Epreuve de stress|Rehaussement tardif|Conclusion)",
        "Technique": r"Technique\s*([\s\S]*?)(?=Indication|Description|Epreuve de stress|Rehaussement tardif|Conclusion)",
        "Description": r"Description\s*([\s\S]*?)(?=Indication|Technique|Epreuve de stress|Rehaussement tardif|Conclusion)",
        "Epreuve de stress": r"Epreuve de stress\s*([\s\S]*?)(?=Indication|Technique|Description|Rehaussement tardif|Conclusion)",
        "Rehaussement tardif": r"Rehaussement tardif\s*([\s\S]*?)(?=Indication|Technique|Description|Epreuve de stress|Conclusion)",
        "Conclusion": r"Conclusion\s*([\s\S]*?)(?=Indication|Technique|Description|Epreuve de stress|Rehaussement tardif)"
    }

    data = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        if match:
            data[field] = match.group(1).strip()
    
    return data

def insert_data_into_elasticsearch(data, index_name='medical_data'):
    try:
        res = es.index(index=index_name, body=data)
        logging.debug(f"Inserted document ID: {res['_id']}")
    except TransportError as e:
        if e.status_code == 429 and 'index has read-only-allow-delete block' in str(e.error):
            # Remove the read-only block
            es.indices.put_settings(index=index_name, body={"index.blocks.read_only_allow_delete": None})
            # Retry inserting the document
            res = es.index(index=index_name, body=data)
            logging.debug(f"Inserted document ID after removing block: {res['_id']}")
        else:
            raise e
        
@app.route('/process_pdf', methods=['GET'])
def process_pdf():
    try:
        with pysftp.Connection(SFTP_HOST, username=SFTP_USERNAME, password=SFTP_PASSWORD, port=SFTP_PORT, cnopts=cnopts) as sftp:
            sftp.cwd('upload')
            pdf_files = [f for f in sftp.listdir() if f.endswith('.pdf')]
            logging.debug(f"File {pdf_files}")
            if not pdf_files:
                return jsonify({"error": "No PDF files found"}), 400
            sftp.get(pdf_files[0], os.path.join(app.config['UPLOAD_FOLDER'], pdf_files[0]))
            pdf_file = os.path.join(app.config['UPLOAD_FOLDER'], pdf_files[0])
            logging.debug(f"2) File {pdf_file}")
            text = extract_text_from_pdf(pdf_file)
            parsed_data = parse_pdf_text(text)
            logging.debug(f"3) parsed_data {parsed_data}")
            insert_data_into_elasticsearch(parsed_data)
            return jsonify({"message": "Data processed and inserted successfully"}), 200
    
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
# Search patients in Elasticsearch
@app.route('/search_patients', methods=['GET'])
def search_patients():
    query = request.args.get('query', '')
    es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT, 'scheme': 'http'}])
    try:
     int_query = int(query)
     is_numeric = True
    except ValueError:
     is_numeric = False
    if is_numeric:
          search_body = {
            "query": {
                "term": {
                "PID:": int_query
                }
            }
    }
    else:
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "Pathology",
                        "PID",
                        "Indication",
                        "Technique",
                        "Description",
                        "Epreuve de stress",
                        "Rehaussement tardif",
                        "Conclusion"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO" 
                }
            }
        }
    response = es.search(index=ES_INDEX, body=search_body)
    return jsonify(response['hits']['hits']), 200

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/sftp')
def sftp():
    return render_template('sftp.html')

if __name__ == '__main__':
    app.run(debug=True)