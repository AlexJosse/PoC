import json
import random
import mysql.connector
from mysql.connector import Error
from faker import Faker

# Function to create a random set of drugs and dosages
def generate_random_drugs():
    drugs_list = ['morphine', 'aspirin', 'ibuprofen', 'acetaminophen', 'penicillin']
    drugs_data = {drug: f"{random.randint(1, 100)}mg" for drug in random.sample(drugs_list, k=random.randint(1, len(drugs_list)))}
    return json.dumps(drugs_data)

def insert_patients(connection, patients):
    cursor = connection.cursor()
    try:
        cursor.executemany(
            """
                INSERT INTO patients (firstname, lastname, address, drugs)
                VALUES (%s, %s, %s, %s)
            """, patients)
        connection.commit()
        print("200 patients inserted")
    except Error as e:
        print(f"The error '{e}' occured")

def create_connection(host_name, port, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            port=port,
            database= db_name
        )
        print("Connection to MySql successful")
    except Error as e:
        print(f"The error '{e}' occured")
    return connection

host_name = "localhost"
port = 3356
user_name = "root"
user_password = "root"
db_name = "hospital"

def execute_query(connection, query):
    cursor = connection.cursor()
    try: 
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occured")

connection_to_db = create_connection(host_name, port, user_name, user_password, db_name)

create_patients_table_query = """
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    drugs JSON NOT NULL
) ENGINE = InnoDB;
"""

if connection_to_db:
    execute_query(connection_to_db, create_patients_table_query)


fake = Faker()

patients = [
    (
        fake.first_name(),
        fake.last_name(),
        fake.address(),
        generate_random_drugs()
    ) for _ in range(200)
]

if connection_to_db: 
    insert_patients(connection_to_db, patients)