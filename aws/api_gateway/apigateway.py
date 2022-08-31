import boto3
import json

client = boto3.client('apigateway')

response = client.get_rest_apis()

response = client.get_rest_api(
    restApiId='i94w71lsq9'
)

print(response)

apis=response.get("items")
for api in apis:
    print(api)
    print("apiName: {} - apiId: {}".format(api.get("name"), api.get("id")))

# print("-------get_base_path_mappings-------")

# response = client.get_base_path_mappings(domainName="api.healthnexus.io")
# print(response)

# print("-------get_rest_api-------")

response_json = json.dumps(response, indent=2)

print(response_json)

