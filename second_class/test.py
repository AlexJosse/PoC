import requests
import random
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Hugging Face API configuration
API_TOKEN = 'x'  # Replace with your Hugging Face API token

# Function to call Hugging Face API with retry logic
def generate_text(prompt, model):
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'inputs': prompt,
        'parameters': {
            'min_lenght': 50000,
            'repetition_penalty': 100
        }
    }
    
    for attempt in range(5):  # Retry up to 5 times
        response = requests.post(f'https://api-inference.huggingface.co/models/{model}', headers=headers, json=data)
        response_json = response.json()
        
        if isinstance(response_json, list) and 'generated_text' in response_json[0]:
            return response_json[0]['generated_text'].strip()
        elif 'estimated_time' in response_json:
            wait_time = response_json['estimated_time']
            logging.warning("Model %s is currently loading. Retrying in %.2f seconds...", model, wait_time)
            time.sleep(wait_time)  # Wait for the estimated time before retrying
        else:
            logging.error("Error in generating text: %s", response_json)
            return "Error in generating text"
    
    return "Error in generating text"

# Generate and display fake data for demonstration
def generate_fake_data():
    logging.info("Generating fake data")

    # Generate multiple patient profiles in a single API call
    patient_prompt = (
        "Generate 10 different random patient profiles with the following details, it's important to have 3 patients: "
        "First name, Last name, Address, Date of Birth, Gender, Phone number, Email. "
        "Provide these details for 10 patients, each of these 10  profile separated by a blank line."
    )
    model = 'meta-llama/Meta-Llama-3-8B-Instruct'
    patient_data = generate_text(patient_prompt, model)
    if "Error" not in patient_data:
        logging.info("Patient Data:\n%s", patient_data)
    else:
        logging.error("Failed to generate patient data")

# Generate and display the data
generate_fake_data()
