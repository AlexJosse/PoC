from flask import Flask, jsonify, request, render_template
import mysql.connector
from mysql.connector import Error
from faker import Faker
from elasticsearch import Elasticsearch

app = Flask(__name__)


# MySQL and Elasticsearch details
MYSQL_HOST = "localhost"
MYSQL_PORT = 3356
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DB = "hospital"
ES_HOST = "localhost"
ES_PORT = 9200
ES_INDEX = "patients"

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
    
@app.route('/insert_patients', methods=['GET'])
def insert_patients():
    fake = Faker('fr_FR')
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
    connection = create_connection_to_db()
    cursor = connection.cursor()
    try:
        cursor.executemany(
            """
            INSERT INTO patients (firstname, lastname, address, note, age, sexe)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, patients)
        connection.commit()
        last_patient_id = cursor.lastrowid
        cursor.execute(f"SELECT * FROM patients where id >= {last_patient_id - 199}")
        inserted_patients = cursor.fetchall()

        return jsonify({"message": f"Patients created successfully,", "data": inserted_patients}),200
    except Error as e:
        print(f"The error '{e}' occurred")

@app.route('/retrieve_patients', methods=['GET'])
def retrieve_patients():
    connection = create_connection_to_db()
    cursor = connection.cursor(dictionary=True)
    try:
      per_page = request.args.get('per_page', 10, type=int)
      query = "SELECT * FROM patients ORDER BY id LIMIT %s"
      cursor.execute(query, (per_page,))
      result = cursor.fetchall()

      cursor.execute("SELECT COUNT(*) FROM patients")
      total_patients = cursor.fetchone()['COUNT(*)']
      total_pages = (total_patients + per_page - 1)

      return jsonify({
          "patients": result,
          "pagination": {
              "per_page": per_page,
              "total_pages": total_pages,
              "total_patients": total_pages
          }
      }), 200
    except Error as e:
        return jsonify({"error": str(e)}), 500

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
                    "lastname",
                    "address",
                    "age",
                    "note"
                ]
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