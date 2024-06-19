from flask import Blueprint, jsonify
from utils.db_utils import create_database
from models import create_connection_to_db
from config import Config

db_bp = Blueprint('db_bp', __name__)

@db_bp.route('/create_database', methods=['GET'])
def create_db():
    connection = create_connection_to_db(Config)
    message = create_database(connection, Config.MYSQL_DB)
    if "error" in message:
        return jsonify({"error": message}), 500
    return jsonify({"message": message}), 200
