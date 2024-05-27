from elasticsearch import Elasticsearch

def search_patients(es, index_name, query):
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": [
                    "firstname",
                    "lastname^10",  # Boost the importance of the last name field by a factor of 10
                    "address",
                    "note"
                ],
                "type": "best_fields"  # This ensures the best matching fields are used
            }
        }
    }
    response = es.search(index=index_name, body=search_body)
    return response['hits']['hits']

def print_patient(patient):
    print(f"ID: {patient.get('id')}")
    print(f"First Name: {patient.get('firstname')}")
    print(f"Last Name: {patient.get('lastname')}")
    print(f"Address: {patient.get('address')}")
    print(f"Note: {patient.get('note')}")
    print(f"Age: {patient.get('age')}")
    print(f"Sex: {patient.get('sexe')}")
    print("-" * 40)

# Elasticsearch details
es_host = "localhost"
es_port = 9200
index_name = "patients"

# Create a connection to Elasticsearch
es = Elasticsearch([{'host': es_host, 'port': es_port, 'scheme': 'http'}])

# Example usage of the search function
if __name__ == "__main__":
    # Define your search query
    search_query = "John"  # Replace with the actual query
    search_results = search_patients(es, index_name, search_query)
    
    # Print out the search results
    print(f"Search results for query '{search_query}':")
    for result in search_results:
        print_patient(result["_source"])
