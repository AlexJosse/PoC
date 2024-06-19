# routes/upload.py
import os
import logging
import pysftp
from flask import Blueprint, request, jsonify, current_app
from config import Config

upload_bp = Blueprint('upload_bp', __name__)

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # Disable host key checking

@upload_bp.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('files')

    if not files or files[0].filename == '':
        return jsonify({"error": "No selected file"}), 400

    upload_results = []

    for file in files:
        if file:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
            logging.debug(f"Saving file to {file_path}")
            try:
                file.save(file_path)
                logging.debug(f"File saved to {file_path}")
                os.chmod(file_path, 0o777)
                logging.debug(f"Permissions set for {file_path}")

                with pysftp.Connection(Config.SFTP_HOST, username=Config.SFTP_USERNAME, password=Config.SFTP_PASSWORD, port=Config.SFTP_PORT, cnopts=cnopts) as sftp:
                    sftp.put(file_path, f'upload/{file.filename}')
                    logging.debug(f"File {file.filename} uploaded to SFTP server")
                upload_results.append(f"File {file.filename} uploaded successfully")
            except Exception as e:
                logging.error(f"Error saving file {file.filename}: {str(e)}")
                return jsonify({"error": str(e)}), 500
            finally:
                os.remove(file_path)
                logging.debug(f"File {file.filename} removed from {file_path}")

    return jsonify({"message": upload_results}), 200
