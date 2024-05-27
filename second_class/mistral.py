import logging
import re
from transformers import pipeline, set_seed, AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Login to Hugging Face
login()

# Initialize the model and tokenizer
model_name = "mistralai/Mistral-7B-Instruct-v0.3"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Initialize the text generation pipeline
generator = pipeline('text-generation', model=model, tokenizer=tokenizer)
set_seed(42)

# Function to generate text using the local model
def generate_text(prompt, max_length=300):
    generated = generator(prompt, max_length=max_length, num_return_sequences=1, truncation=True)
    return generated[0]['generated_text'].strip()

# Generate and display a single fake patient profile
def generate_single_patient_profile():
    logging.info("Generating a single patient profile")

    # Generate a single patient profile
    patient_prompt = (
        "Generate a random patient profile with the following details:\n"
        "First name: [First name]\n"
        "Last name: [Last name]\n"
        "Address: [Address]\n"
        "Date of Birth: [DD.MM.YYYY]\n"
        "Gender: [Male/Female]\n"
        "Phone number: [Phone number]\n"
        "Email: [Email]\n"
        "\n"
        "Example:\n"
        "First name: John\n"
        "Last name: Doe\n"
        "Address: 1234 Elm St, Springfield, IL\n"
        "Date of Birth: 01.01.1990\n"
        "Gender: Male\n"
        "Phone number: 555-1234\n"
        "Email: john.doe@example.com\n\n"
        "Now, generate another random patient profile with the following details:\n"
        "First name:"
    )
    patient_data = generate_text(patient_prompt, max_length=300)
    logging.info("Patient Data:\n%s", patient_data)
    
    # Process the generated data
    match = re.search(r"First name: (.+)\nLast name: (.+)\nAddress: (.+)\nDate of Birth: (\d{2}\.\d{2}\.\d{4})\nGender: (Male|Female)\nPhone number: (.+)\nEmail: (.+)", patient_data)
    if match:
        first_name, last_name, address, date_of_birth, gender, phone, email = match.groups()
        patient_record = {
            "first_name": first_name,
            "last_name": last_name,
            "address": address,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "phone": phone,
            "email": email
        }
        logging.info("Processed Patient: %s", patient_record)
    else:
        logging.warning("Could not parse profile: %s", patient_data)

# Generate and display the single patient profile
generate_single_patient_profile()
