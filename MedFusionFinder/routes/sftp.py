from flask import Blueprint
from services.sftp_service import test_sftp_connection, list_files
from config import Config

sftp_bp = Blueprint('sftp_bp', __name__)

@sftp_bp.route('/test_sftp_connection', methods=['GET'])
def test_sftp_conn():
    return test_sftp_connection(Config)

@sftp_bp.route('/list_files', methods=['GET'])
def list_sftp_files():
    return list_files(Config)
