import mysql.connector
from mysql.connector import Error
from elasticsearch import Elasticsearch, helpers
import json

def create_connection(host_name, port, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            port=port,
            database=db_name
        )
        print("Connection to MySql successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

host_name = "localhost"
port = 3356
user_name = "root"
user_password = "root"
db_name = "hospital"

def retrieve_patients(connection):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * from patients')
        result = cursor.fetchall()
        print("Retrieved the patients data successfully")
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
        return []

def create_index(es, index_name):
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
                "drugs": {"type": "object"}  # Changed to 'object'
            }
        }
    }
    es.indices.create(index=index_name, body=settings)
    print(f"Index '{index_name}' created successfully")

def prepare_patients_data(patients):
    for patient in patients:
        if 'drugs' in patient and isinstance(patient['drugs'], str):
            try:
                patient['drugs'] = json.loads(patient['drugs'])
            except json.JSONDecodeError:
                patient['drugs'] = {}
    return patients

def insert_patient_data_to_es(es, index_name, patients):
    actions = [
        {
            "_index": index_name,
            "_source": patient
        }
        for patient in patients
    ]

    success, failed = helpers.bulk(es, actions, raise_on_error=False)
    
    print(f"Successfully inserted {success} documents")
    if failed:
        print(f"Failed to insert {len(failed)} documents:")
        for item in failed:
            print(item)
    print(f"Data insertion into ES complete")

connection_to_db = create_connection(host_name, port, user_name, user_password, db_name)

if connection_to_db:
    patients = retrieve_patients(connection_to_db)
    patients = prepare_patients_data(patients)

es_host = "localhost"
es_port = 9200
index_name = "patients"

es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': 'http'}])

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
create_index(es, index_name)

insert_patient_data_to_es(es, index_name, patients)