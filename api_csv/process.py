@app.route('/process_csv', methods=['GET'])
def process_csv():
    try:
        # Connect to SFTP and download the file
        with pysftp.Connection(SFTP_HOST, username=SFTP_USERNAME, password=SFTP_PASSWORD, port=SFTP_PORT, cnopts=cnopts) as sftp:
            sftp.cwd('upload')
            csv_files = [f for f in sftp.listdir() if f.endswith('.csv')]
            if not csv_files:
                return jsonify({"error": "No CSV files found"}), 400
            sftp.get(csv_files[0], os.path.join(app.config['UPLOAD_FOLDER'], csv_files[0]))

        # Load the CSV file
        csv_file = os.path.join(app.config['UPLOAD_FOLDER'], csv_files[0])
        data = pd.read_csv(csv_file)

        # Function to extract diseases from descriptions using Hugging Face API
        def extract_diseases(description):
            headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
            payload = {"inputs": description}
            response = requests.post(HF_API_URL, headers=headers, json=payload)
            if response.status_code == 200:
                entities = response.json()
                diseases = [entity['word'] for entity in entities if 'disease' in entity['entity'].lower()]
                return ", ".join(diseases)
            else:
                logging.error(f"Error from Hugging Face API: {response.status_code} {response.text}")
                return ""

        # Function to generate Elasticsearch documents from CSV rows
        def generate_docs(data):
            for index, row in data.iterrows():
                pid = str(row[0]).zfill(10)
                description = row[2] if len(row) > 2 else ""
                diseases = extract_diseases(description)

                doc = {
                    "_index": ES_INDEX,
                    "_id": pid,
                    "_source": {
                        "pid": pid,
                        "description": description,
                        "diseases": diseases
                    }
                }
                yield doc

        # Insert data into Elasticsearch
        # helpers.bulk(es, generate_docs(data))
        return jsonify({"message": "Data processed and inserted successfully", "data": data}), 200

    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")
        return jsonify({"error": str(e)}), 500