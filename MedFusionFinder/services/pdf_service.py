# services/pdf_service.py
import os
import logging
import pysftp
from utils.pdf_utils import extract_text_from_pdf, parse_pdf_text
from services.es_service import insert_data_into_elasticsearch

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # Disable host key checking

def process_service_pdf(config, es):
    try:
        with pysftp.Connection(config.SFTP_HOST, username=config.SFTP_USERNAME, password=config.SFTP_PASSWORD, port=config.SFTP_PORT, cnopts=cnopts) as sftp:
            sftp.cwd('upload')
            pdf_files = [f for f in sftp.listdir() if f.endswith('.pdf')]
            if not pdf_files:
                return {"error": "No PDF files found", "status_code": 400}
            
            for pdf_file_name in pdf_files:
                local_pdf_path = os.path.join(config.UPLOAD_FOLDER, pdf_file_name)
                sftp.get(pdf_file_name, local_pdf_path)
                text = extract_text_from_pdf(local_pdf_path)
                parsed_data = parse_pdf_text(text)
                insert_data_into_elasticsearch(es, parsed_data)
                logging.info(f"Processed and inserted data from {pdf_file_name}")

            return {"message": "All PDF files processed and inserted successfully", "status_code": 200}
    except Exception as e:
        logging.error(f"Error processing PDFs: {str(e)}")
        return {"error": str(e), "status_code": 500}
