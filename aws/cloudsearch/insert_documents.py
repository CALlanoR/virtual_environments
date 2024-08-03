import boto3
import json
import random

client = boto3.client("cloudsearchdomain", 
                      endpoint_url="http://doc-llano-fac-poc.us-east-1.cloudsearch.amazonaws.com")

print("cloudsearchdomain connected...")

npis_list1 = random.sample(range(1000000000, 8000000000), 60000)
npis_list2 = random.sample(range(8000000000, 9000000000), 100000)

npis_list_str1 = " ".join(str(npi) for npi in npis_list1)
npis_list_str2 = " ".join(str(npi) for npi in npis_list2)

# print(npis_list_str1)

print("------")

facs = [
    {
        "type": "add",
        "id": 1,
        "fields": {
            "dbname": "hospital1",
            "entitytype": "COO",
            "hcoplid": "1234567",
            "idtypecd": "COO",
            "idvalue": "9876543210",
            "npis1": npis_list_str1,
            "npis2": "1 2 3"
        }
    },
    {
        "type": "add",
        "id": 2,
        "fields": {
            "dbname": "hospital2",
            "entitytype": "COO",
            "hcoplid": "876543",
            "idtypecd": "COO",
            "idvalue": "654394384",
            "npis1": npis_list_str2,
            "npis2": "1 2 3"
        }
    }
]

print(facs)

print("------")

cloudsearch_upload_response = client.upload_documents(
    documents=json.dumps(facs).encode(),
    contentType="application/json"
)

print(cloudsearch_upload_response)


# response = client.search(
#     query="hospital1", 
#     size = 10
# )

# print(response)

