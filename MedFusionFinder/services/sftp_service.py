import pysftp
import os
import logging
from flask import jsonify
from config import Config  # Import the config module

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # Disable host key checking

def test_sftp_connection(config):
    try:
        with pysftp.Connection(config.SFTP_HOST, username=config.SFTP_USERNAME, password=config.SFTP_PASSWORD, port=config.SFTP_PORT, cnopts=cnopts) as sftp:
            sftp.listdir('.')
            return jsonify({"message": "Connection to SFTP server successful"}), 200
    except Exception as e:
        logging.error(f"Error testing SFTP connection: {str(e)}")
        return jsonify({"error": str(e)}), 500

def list_files(config):
    try:
        with pysftp.Connection(config.SFTP_HOST, username=config.SFTP_USERNAME, password=config.SFTP_PASSWORD, port=config.SFTP_PORT, cnopts=cnopts) as sftp:
            sftp.cwd('upload')
            files = sftp.listdir()
        return jsonify({"files": files}), 200
    except Exception as e:
        logging.error(f"Error listing files: {str(e)}")
        return jsonify({"error": str(e)}), 500
