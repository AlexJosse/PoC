from elasticsearch import Elasticsearch, TransportError, helpers
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

def clean_elasticsearch_index(es, index_name='medical_data'):
    try:
        helpers.bulk(es, [
            {"_op_type": "delete", "_index": index_name, "_id": doc['_id']}
            for doc in helpers.scan(es, index=index_name, _source=False)
        ])
        return {"message": f"All documents in index '{index_name}' have been deleted."}
    except TransportError as e:
        if e.status_code == 404:
            return {"error": f"Index '{index_name}' not found."}
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

def map_patient_to_es(patient):
    return {
        "PID": patient["PID"],
        "Birthdate": patient["date_of_birth"],
        "Adress": patient["address"]
    }

def insert_data_into_es_sql(es, patients):
    actions = [
        {
            "_index": "medical_data",
            "_id": patient['id'],
            "_source": map_patient_to_es(patient)
        }
        for patient in patients
    ]

    try:
        helpers.bulk(es, actions)
        return {"message": "Data inserted successfully"}
    except Exception as e:
        return {"error": str(e)}
