from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from faker import Faker
from elasticsearch import Elasticsearch, helpers

app = Flask(__name__)
CORS(app)

# MySQL and Elasticsearch details
MYSQL_HOST = "localhost"
MYSQL_PORT = 3356
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DB = "hospital"
ES_HOST = "localhost"
ES_PORT = 9200
ES_INDEX = "patients"

# Establish connection to MySQL
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

# Create the database
@app.route('/create_database', methods=['POST'])
def create_database():
    connection = create_connection_to_db()
    query = f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}"
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        return jsonify({"message": "Database created successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Create the patients table
@app.route('/create_table', methods=['POST'])
def create_table():
    connection = create_connection_to_db()
    query = """
    CREATE TABLE IF NOT EXISTS patients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        firstname VARCHAR(255) NOT NULL,
        lastname VARCHAR(255) NOT NULL,
        address VARCHAR(255) NOT NULL,
        note TEXT,
        age INT,
        sexe ENUM('male', 'female', 'other') NOT NULL
    ) ENGINE = InnoDB;
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        return jsonify({"message": "Table created successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Insert patients
@app.route('/insert_patients', methods=['POST'])
def insert_patients():
    connection = create_connection_to_db()
    fake = Faker()
    patients = [
        (
            fake.first_name(),
            fake.last_name(),
            fake.address(),
            fake.text(),
            fake.random_int(min=0, max=100),
            fake.random_element(elements=('male', 'female'))
        ) for _ in range(200)
    ]
    cursor = connection.cursor()
    query = """
    INSERT INTO patients (firstname, lastname, address, note, age, sexe)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.executemany(query, patients)
        connection.commit()
        return jsonify({"message": "200 patients inserted successfully"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Retrieve patients
@app.route('/retrieve_patients', methods=['GET'])
def retrieve_patients():
    connection = create_connection_to_db()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM patients")
        result = cursor.fetchall()
        return jsonify(result), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Create Elasticsearch index
def create_index(es):
    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "firstname": {"type": "text"},
                "lastname": {"type": "text"},
                "address": {"type": "text"},
                "note": {"type": "text"},
                "age": {"type": "integer"},
                "sexe": {"type": "keyword"}
            }
        }
    }
    es.indices.create(index=ES_INDEX, body=settings)
    print(f"Index '{ES_INDEX}' created successfully")

# Insert data into Elasticsearch
def insert_data_to_elasticsearch(es, data):
    actions = [
        {
            "_index": ES_INDEX,
            "_source": patient
        }
        for patient in data
    ]
    helpers.bulk(es, actions)
    print(f"Inserted {len(data)} records into Elasticsearch index '{ES_INDEX}'")

# Retrieve and index patients in Elasticsearch
@app.route('/index_patients', methods=['POST'])
def index_patients():
    connection = create_connection_to_db()
    es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT, 'scheme': 'http'}])
    if es.indices.exists(index=ES_INDEX):
        es.indices.delete(index=ES_INDEX)
    create_index(es)
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM patients")
        result = cursor.fetchall()
        insert_data_to_elasticsearch(es, result)
        return jsonify({"message": "Patients indexed in Elasticsearch"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Search patients in Elasticsearch
@app.route('/search_patients', methods=['GET'])
def search_patients():
    query = request.args.get('query', '')
    es = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT, 'scheme': 'http'}])
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": [
                    "firstname",
                    "lastname^10",
                    "address",
                    "note"
                ],
                "type": "best_fields"
            }
        }
    }
    response = es.search(index=ES_INDEX, body=search_body)
    return jsonify(response['hits']['hits']), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
