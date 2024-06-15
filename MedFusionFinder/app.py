from flask import Flask, jsonify, request, render_template
import mysql.connector
from mysql.connector import Error
import pysftp
from faker import Faker
from elasticsearch import Elasticsearch
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
ES_HOST = os.getenv('ES_HOST', 'localhost')
ES_PORT = int(os.getenv('ES_PORT', 9200))
ES_INDEX = os.getenv('ES_INDEX', 'patients')


# SFTP details
SFTP_HOST = os.getenv('SFTP_HOST', 'sftp')
SFTP_PORT = int(os.getenv('SFTP_PORT', 22))
SFTP_USERNAME = os.getenv('SFTP_USERNAME', 'sftpuser')
SFTP_PASSWORD = os.getenv('SFTP_PASSWORD', 'password')

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

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/sftp')
def sftp():
    return render_template('sftp.html')

if __name__ == '__main__':
    app.run(debug=True)