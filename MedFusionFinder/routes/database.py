from flask import Blueprint, jsonify, request
from utils.db_utils import create_database
from models import create_connection_to_db, create_patients_table, create_patients_fake_data, create_relation_between_patient_pid, create_patients_relation_pid_table, search_patient
from config import Config

db_bp = Blueprint('db_bp', __name__)

@db_bp.route('/create_database', methods=['GET'])
def create_db():
    connection = create_connection_to_db(Config)
    message = create_database(connection, Config.MYSQL_DB)
    if "error" in message:
        return jsonify({"error": message}), 500
    return jsonify({"message": message}), 200

@db_bp.route('/init_project_database', methods=['GET'])
def init_project_database():
    message = create_patients_table(Config)
    if "error" in message:
        return jsonify({"error": message}), 500
    message = create_patients_fake_data(Config)
    if "error" in message:
        return jsonify({"error": message}), 500
    message = create_patients_relation_pid_table(Config)
    if "error" in message:
         return jsonify({"error": message}), 500
    message = create_relation_between_patient_pid(Config)
    if "error" in message:
         return jsonify({"error": message}), 500
    return jsonify({"message": message}), 200

@db_bp.route('/search_patient_by_name', methods=['GET'])
def search_patient_by_name():
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    result = search_patient(Config, first_name, last_name)
    
    if isinstance(result, str) and "error" in result:
        return jsonify({"error": result}), 500
    
    return jsonify({"result": result}), 200