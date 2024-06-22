from mysql.connector import connect, Error
from faker import Faker

def create_connection_to_db(config):
    connection = None
    try:
        connection = connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            passwd=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB,
            port=config.MYSQL_PORT
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def create_patients_table(config):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS patients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth DATE NOT NULL,
        gender TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL
    );
    """
    connection = create_connection_to_db(config)
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute(create_table_query)
            connection.commit()
        except Error as e:
            print(f"The error '{e}' occurred")
            return str(e)
        finally:
            cursor.close()
            connection.close()
            return f"Database created successfully"
    else:
        print("Failed to create the database connection")
        return str(e)
    
def create_patients_fake_data(config):
    fake = Faker('fr_FR')
    connection = create_connection_to_db(config)
    if connection is not None:
        try:
            cursor = connection.cursor()
            insert_query = """
            INSERT INTO patients (first_name, last_name, date_of_birth, gender, address, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            for _ in range(5500):
                first_name = fake.first_name()
                last_name = fake.last_name()
                date_of_birth = fake.date_of_birth(minimum_age=0, maximum_age=110)
                gender = fake.random_element(elements=("M", "F"))
                address = fake.address()
                phone = fake.phone_number()
                email = fake.email()
                cursor.execute(insert_query, (first_name, last_name, date_of_birth, gender, address, phone, email))
            connection.commit()
            print("5500 fake patient records inserted successfully")
            return "5500 fake patient records inserted successfully"
        except Error as e:
            print(f"The error '{e}' occurred")
            return str(e)
        finally:
            cursor.close()
            connection.close()
    else:
        print("Failed to create the database connection")
        return "Failed to create the database connection"

def create_patients_relation_pid_table(config):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS patients_relation_pid (
        id INT AUTO_INCREMENT PRIMARY KEY,
        PID BIGINT,
        patient_id INT,
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    );
    """

    connection = create_connection_to_db(config)
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute(create_table_query)
            connection.commit()
            return "Patients relation PID table created successfully"
        except Error as e:
            print(f"The error '{e}' occurred")
            return str(e)
        finally:
            cursor.close()
            connection.close()
    else:
        print("Failed to create the database connection")
        return "Failed to create the database connection"

    
def create_relation_between_patient_pid(config):
    connection = create_connection_to_db(config)
    if connection is not None:
        try:
            cursor = connection.cursor()

            with open('uniq_pids.txt', 'r') as file:
                pids = [line.strip() for line in file.readlines()]

            # Fetch patient IDs
            cursor.execute("SELECT id FROM patients")
            patient_ids = [row[0] for row in cursor.fetchall()]

            # Check if there are more PIDs than patients
            if len(pids) > len(patient_ids):
                return "More PIDs than patients. Unable to create relations."

            # Insert relationships
            insert_query = "INSERT INTO patients_relation_pid (PID, patient_id) VALUES (%s, %s)"
            for pid, patient_id in zip(pids, patient_ids):
                cursor.execute(insert_query, (pid, patient_id))

            connection.commit()
            return "Relationships between patients and PIDs created successfully"
        except Error as e:
            print(f"The error '{e}' occurred")
            return str(e)
        finally:
            cursor.close()
            connection.close()
    else:
        print("Failed to create the database connection")
        return "Failed to create the database connection"

def search_patient(config, first_name=None, last_name=None):
    connection = create_connection_to_db(config)
    if connection is not None:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
            SELECT p.pid, p.first_name, p.last_name
            FROM patients_relation_pid prp
            JOIN patients p ON prp.patient_id = p.id
            WHERE (%s IS NULL OR p.first_name = %s)
            AND (%s IS NULL OR p.last_name = %s)
            """
            cursor.execute(query, (first_name, first_name, last_name, last_name))
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")
            return str(e)
        finally:
            cursor.close()
            connection.close()
    else:
        print("Failed to create the database connection")
        return "Failed to create the database connection"