import mysql.connector
from mysql.connector import errorcode

# Database configuration
config = {
  'user': 'myuser',
  'password': 'root',
  'host': '127.0.0.1',
  'port': '3356',
  'database': 'hospital'
}

# Create tables SQL
TABLES = {}
TABLES['Departments'] = (
    "CREATE TABLE Departments ("
    "  department_id INT PRIMARY KEY,"
    "  name VARCHAR(50),"
    "  location VARCHAR(50),"
    "  phone VARCHAR(15)"
    ")")

TABLES['Insurance'] = (
    "CREATE TABLE Insurance ("
    "  insurance_id INT PRIMARY KEY,"
    "  provider_name VARCHAR(50),"
    "  policy_number VARCHAR(50),"
    "  coverage_details VARCHAR(100)"
    ")")

TABLES['Patients'] = (
    "CREATE TABLE Patients ("
    "  patient_id INT PRIMARY KEY,"
    "  first_name VARCHAR(50),"
    "  last_name VARCHAR(50),"
    "  date_of_birth DATE,"
    "  gender CHAR(1),"
    "  address VARCHAR(100),"
    "  phone VARCHAR(15),"
    "  email VARCHAR(50),"
    "  insurance_id INT,"
    "  FOREIGN KEY (insurance_id) REFERENCES Insurance(insurance_id)"
    ")")

TABLES['Doctors'] = (
    "CREATE TABLE Doctors ("
    "  doctor_id INT PRIMARY KEY,"
    "  first_name VARCHAR(50),"
    "  last_name VARCHAR(50),"
    "  specialty VARCHAR(50),"
    "  phone VARCHAR(15),"
    "  email VARCHAR(50),"
    "  department_id INT,"
    "  FOREIGN KEY (department_id) REFERENCES Departments(department_id)"
    ")")

TABLES['Appointments'] = (
    "CREATE TABLE Appointments ("
    "  appointment_id INT PRIMARY KEY,"
    "  patient_id INT,"
    "  doctor_id INT,"
    "  appointment_date DATE,"
    "  appointment_time TIME,"
    "  reason VARCHAR(100),"
    "  status VARCHAR(20),"
    "  FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),"
    "  FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)"
    ")")

TABLES['MedicalRecords'] = (
    "CREATE TABLE MedicalRecords ("
    "  record_id INT PRIMARY KEY,"
    "  patient_id INT,"
    "  doctor_id INT,"
    "  record_date DATE,"
    "  diagnosis VARCHAR(100),"
    "  treatment VARCHAR(100),"
    "  notes TEXT,"
    "  FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),"
    "  FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)"
    ")")

TABLES['Prescriptions'] = (
    "CREATE TABLE Prescriptions ("
    "  prescription_id INT PRIMARY KEY,"
    "  record_id INT,"
    "  medication VARCHAR(50),"
    "  dosage VARCHAR(20),"
    "  start_date DATE,"
    "  end_date DATE,"
    "  instructions TEXT,"
    "  FOREIGN KEY (record_id) REFERENCES MedicalRecords(record_id)"
    ")")

TABLES['PatientDoctors'] = (
    "CREATE TABLE PatientDoctors ("
    "  patient_doctor_id INT PRIMARY KEY,"
    "  patient_id INT,"
    "  doctor_id INT,"
    "  FOREIGN KEY (patient_id) REFERENCES Patients(patient_id),"
    "  FOREIGN KEY (doctor_id) REFERENCES Doctors(doctor_id)"
    ")")

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(config['database']))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

def create_tables(cursor):
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

# Connect to MySQL
try:
    cnx = mysql.connector.connect(user=config['user'], password=config['password'], host=config['host'], port=config['port'])
    cursor = cnx.cursor()

    # Create database
    try:
        cnx.database = config['database']
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            cnx.database = config['database']
        else:
            print(err)
            exit(1)

    # Create tables
    create_tables(cursor)

    # Close cursor and connection
    cursor.close()
    cnx.close()

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)
