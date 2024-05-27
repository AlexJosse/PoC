import mysql.connector
from mysql.connector import Error
from elasticsearch import Elasticsearch, helpers
import json

def create_connection_to_db(host_name, user_name, user_password, db_name, port):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
            port=port
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def retrieve_patients(connection):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM patients")
        result = cursor.fetchall()
        print("Retrieved patients successfully")
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
        return []

def create_index(es, index_name):
    # Define the index settings and mappings
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
    es.indices.create(index=index_name, body=settings)
    print(f"Index '{index_name}' created successfully")

def insert_data_to_elasticsearch(es, index_name, data):
    actions = [
        {
            "_index": index_name,
            "_source": patient
        }
        for patient in data
    ]
    helpers.bulk(es, actions)
    print(f"Inserted {len(data)} records into Elasticsearch index '{index_name}'")

# MySQL container details
host_name = "localhost"
port = 3356
user_name = "root"
user_password = "root"
db_name = "hospital"

# Elasticsearch details
es_host = "localhost"
es_port = 9200
index_name = "patients"

# Create a connection to the MySQL database
connection_to_db = create_connection_to_db(host_name, user_name, user_password, db_name, port)

# Retrieve all patients
patients = []
if connection_to_db:
    patients = retrieve_patients(connection_to_db)

# Create a connection to Elasticsearch  
es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': 'http'}])

# Create an index on Elasticsearch
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
create_index(es, index_name)

# Insert data into Elasticsearch
insert_data_to_elasticsearch(es, index_name, patients)
