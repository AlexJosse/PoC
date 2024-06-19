from elasticsearch import Elasticsearch, TransportError
from config import Config  # Import the config module

def create_es_client(config):
    return Elasticsearch([{'host': config.ES_HOST, 'port': config.ES_PORT}])

def insert_data_into_elasticsearch(es, data, index_name='medical_data'):
    try:
        res = es.index(index=index_name, body=data)
        return res['_id']
    except TransportError as e:
        if e.status_code == 429 and 'index has read-only-allow-delete block' in str(e.error):
            es.indices.put_settings(index=index_name, body={"index.blocks.read_only_allow_delete": None})
            res = es.index(index=index_name, body=data)
            return res['_id']
        else:
            raise e

def search_patients(es, query, index_name='medical_data'):
    try:
        int_query = int(query)
        is_numeric = True
    except ValueError:
        is_numeric = False

    if is_numeric:
        search_body = {
            "query": {
                "term": {
                    "PID:": int_query
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

    response = es.search(index=index_name, body=search_body)
    return response['hits']['hits']
