# routes/csv.py
from flask import Blueprint, jsonify, request
import pysftp
from flask import Blueprint, jsonify, current_app
from config import Config
from elasticsearch import Elasticsearch

csv_bp = Blueprint('csv_bp', __name__)

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # Disable host key checking

es = Elasticsearch([{'host': Config.ES_HOST, 'port': Config.ES_PORT}])


search_bp = Blueprint('search_bp', __name__)

# Search patients in Elasticsearch
@search_bp.route('/search_patients', methods=['GET'])
def search_patients():
    query = request.args.get('query', '')
    es = Elasticsearch([{'host': Config.ES_HOST, 'port': Config.ES_PORT, 'scheme': 'http'}])
    try:
     int_query = int(query)
     is_numeric = True
    except ValueError:
     is_numeric = False
    if is_numeric:
          search_body = {
            "query": {
                "term": {
                "PID": int_query
                }
            }
    }
    else:
        search_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "Pathology",
                        "PID",
                        "Indication",
                        "Technique",
                        "Description",
                        "Epreuve de stress",
                        "Rehaussement tardif",
                        "Conclusion"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO" 
                }
            }
        }
    response = es.search(index=Config.ES_INDEX, body=search_body)
    print(response)
    return jsonify(response['hits']['hits']), 200
