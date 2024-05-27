from elasticsearch import Elasticsearch


def fuzzy_query(es, index_name, field, value, fuzziness="AUTO"):
    search_body = {
        "query": {
            "fuzzy": {
                field: {
                    "value": value,
                    "fuzziness": fuzziness
                }
            }
        }
    }

    response = es.search(index=index_name, body=search_body)
    return response['hits']['hits']


def search_patients(es, index_name, query):
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": [
                    "firstname",
                    "lastname",
                    "address",
                    "drugs"
                ],
                "type": "best_fields"
            }
        }
    }

    reponse = es.search(index=index_name, body=search_body)
    return reponse['hits']['hits']

def print_patient(patient):
    print(f"ID: {patient.get('id')}")
    print(f"First Name: {patient.get('firstname')}")
    print(f"Last Name: {patient.get('lastname')}")
    print(f"Address: {patient.get('address')}")
    print(f"Drug: {patient.get('drugs')}")
    print("-" * 40)

es_host = "localhost"
es_port = 9200
index_name = "patients"

es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': 'http'}])

search_field = "firstname"
search_query = "Alexandre"
fuzziness_level = "AUTO"

search_results = fuzzy_query(es, index_name, search_field, search_query, fuzziness_level)

if search_results:
    for result in search_results:
        print_patient(result["_source"])
else:
    print("No results found for the fuzzy query.")