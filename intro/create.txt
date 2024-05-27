import mysql.connector
from mysql.connector import Error
from faker import Faker

def create_connection(host_name, user_name, user_password, port):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            port=port
        )
        print("Connection to MySQL successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

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

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def insert_patients(connection, patients):
    cursor = connection.cursor()
    try:
        cursor.executemany(
            """
            INSERT INTO patients (firstname, lastname, address, note, age, sexe)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, patients)
        connection.commit()
        print("200 patients inserted successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

# MySQL container details
host_name = "localhost"
port = 3356
user_name = "root"
user_password = "root"
db_name = "hospital"

# SQL statements
create_database_query = f"CREATE DATABASE IF NOT EXISTS {db_name}"
create_patients_table_query = """
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

# Create a connection to the MySQL server
connection = create_connection(host_name, user_name, user_password, port)

# Create the database if it does not exist
if connection:
    create_database(connection, create_database_query)

# Create a connection to the newly created database
connection_to_db = create_connection_to_db(host_name, user_name, user_password, db_name, port)

# Execute the query to create the patients table
if connection_to_db:
    execute_query(connection_to_db, create_patients_table_query)

# Generate 200 random patients
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

# Insert the generated patients into the table
if connection_to_db:
    insert_patients(connection_to_db, patients)
