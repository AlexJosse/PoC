import requests
import random
import mysql.connector
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Hugging Face API configuration
API_TOKEN = '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'  # Replace with your Hugging Face API token

# Function to call Hugging Face API with retry logic
def generate_text(prompt, model, max_length=20):
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'inputs': prompt,
        'options': {
            'max_length': max_length,
            'num_return_sequences': 1
        }
    }
    
    for attempt in range(5):  # Retry up to 5 times
        response = requests.post(f'https://api-inference.huggingface.co/models/{model}', headers=headers, json=data)
        response_json = response.json()
        
        if isinstance(response_json, list):
            return response_json[0]['generated_text'].strip()
        elif 'estimated_time' in response_json:
            wait_time = response_json['estimated_time']
            logging.warning("Model %s is currently loading. Retrying in %.2f seconds...", model, wait_time)
            time.sleep(wait_time)  # Wait for the estimated time before retrying
        else:
            logging.error("Error in generating text: %s", response_json)
            return "Error in generating text"
    
    return "Error in generating text"

# Truncate text to fit within the column length
def truncate_text(text, max_length):
    return text[:max_length].strip()

# Database configuration
config = {
  'user': 'myuser',
  'password': 'root',
  'host': '127.0.0.1',
  'port': '3356',
  'database': 'hospital'
}

# Connect to MySQL
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

# Function to clear existing data from tables
def clear_tables():
    logging.info("Clearing existing data from tables")
    tables = ['MedicalRecords', 'Patients', 'Doctors', 'Insurance', 'Departments']
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
    logging.info("Existing data cleared")

# Generate fake data for Departments table
def generate_departments_data():
    logging.info("Generating departments data")
    departments = ["Cardiology", "Neurology", "Pediatrics", "General Practice", "Orthopedics"]
    for department_id, name in enumerate(departments, start=1):
        location = f"Building {random.choice(['A', 'B', 'C', 'D', 'E'])}"
        phone = f"+41 {random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
        
        cursor.execute(
            "INSERT INTO Departments (department_id, name, location, phone) VALUES (%s, %s, %s, %s)",
            (department_id, name, location, phone)
        )
    logging.info("Departments data generated")

# Generate fake data for Insurance table
def generate_insurance_data():
    logging.info("Generating insurance data")
    for insurance_id in range(1, 11):  # Generate 10 insurance records
        provider_name = truncate_text(generate_text("Nom de la compagnie d'assurance:", 'dbddv01/gpt2-french-small'), 50)
        policy_number = f"POL{random.randint(1000, 9999)}"
        coverage_details = truncate_text(generate_text("Détails de la couverture:", 'dbddv01/gpt2-french-small'), 100)

        cursor.execute(
            "INSERT INTO Insurance (insurance_id, provider_name, policy_number, coverage_details) VALUES (%s, %s, %s, %s)",
            (insurance_id, provider_name, policy_number, coverage_details)
        )
    logging.info("Insurance data generated")

# Helper function to randomly select a language and generate text
def generate_text_in_random_language(prompt_french, prompt_german, prompt_italian):
    languages = [
        ('French', 'dbddv01/gpt2-french-small', prompt_french),
        ('German', 'dbmdz/german-gpt2', prompt_german),
        ('Italian', 'dbmdz/german-gpt2', prompt_italian)  # Using the same model for Italian for simplicity
    ]
    selected_language, model, prompt = random.choice(languages)
    return truncate_text(generate_text(prompt, model), 50)

# Generate fake data for Patients table
def generate_patient_data():
    logging.info("Generating patient data")
    for _ in range(10):  # Generate 10 patients
        patient_id = random.randint(1, 10000)
        first_name = generate_text_in_random_language("Prénom:", "Vorname:", "Nome:")
        last_name = generate_text_in_random_language("Nom de famille:", "Nachname:", "Cognome:")
        date_of_birth = f"{random.randint(1940, 2010)}-{random.randint(1, 12)}-{random.randint(1, 28)}"
        gender = random.choice(['M', 'F'])
        address = generate_text_in_random_language("Adresse:", "Adresse:", "Indirizzo:")
        phone = f"+41 {random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
        email = f"user{patient_id}@example.com"
        insurance_id = random.randint(1, 10)

        cursor.execute(
            "INSERT INTO Patients (patient_id, first_name, last_name, date_of_birth, gender, address, phone, email, insurance_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (patient_id, first_name, last_name, date_of_birth, gender, address, phone, email, insurance_id)
        )
    logging.info("Patient data generated")

# Generate fake data for Doctors table
def generate_doctor_data():
    logging.info("Generating doctor data")
    specialties = ["Cardiologie", "Neurologie", "Pédiatrie", "Médecine générale", "Orthopédie"]
    for _ in range(5):  # Generate 5 doctors
        doctor_id = random.randint(1, 10000)
        first_name = generate_text_in_random_language("Prénom:", "Vorname:", "Nome:")
        last_name = generate_text_in_random_language("Nom de famille:", "Nachname:", "Cognome:")
        specialty = random.choice(specialties)
        phone = f"+41 {random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
        email = f"doctor{doctor_id}@example.com"
        department_id = random.randint(1, 5)

        cursor.execute(
            "INSERT INTO Doctors (doctor_id, first_name, last_name, specialty, phone, email, department_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (doctor_id, first_name, last_name, specialty, phone, email, department_id)
        )
    logging.info("Doctor data generated")

# Generate complex text-based data using Hugging Face
def generate_medical_records():
    logging.info("Generating medical records data")
    for _ in range(5):  # Generate 5 medical records
        record_id = random.randint(1, 10000)
        patient_id = random.randint(1, 10000)
        doctor_id = random.randint(1, 10000)
        record_date = f"{random.randint(2020, 2024)}-{random.randint(1, 12)}-{random.randint(1, 28)}"
        diagnosis = generate_text_in_random_language("Le patient présente des symptômes de", "Der Patient zeigt Symptome von", "Il paziente presenta sintomi di")
        treatment = generate_text_in_random_language("Le traitement recommandé inclut", "Die empfohlene Behandlung umfasst", "Il trattamento raccomandato include")
        notes = generate_text_in_random_language("Notes supplémentaires:", "Zusätzliche Notizen:", "Note aggiuntive:")

        cursor.execute(
            "INSERT INTO MedicalRecords (record_id, patient_id, doctor_id, record_date, diagnosis, treatment, notes) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (record_id, patient_id, doctor_id, record_date, diagnosis, treatment, notes)
        )
    logging.info("Medical records data generated")

# Call the functions to clear existing data and generate new data
clear_tables()
generate_departments_data()
generate_insurance_data()
generate_patient_data()
#generate_doctor_data()
#generate_medical_records()

# Commit the transaction
cnx.commit()

# Close the cursor and connection
cursor.close()
cnx.close()
