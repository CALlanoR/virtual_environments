import boto3
import json
from datetime import datetime, timedelta
import time

client = boto3.client('logs')

query = 'fields @timestamp, @message | parse @message "[*] *" as loggingType, loggingMessage'

# log_group = 'API-Gateway-Execution-Logs_adnaeb0et1/dev'   # HealthNexus HCO VEND API
log_group = 'ApiGatewayAccessLogs'
# log_group = '/ecs/hco-vend_dev'                         # ECS HCO Vend

start_query_response = client.start_query(
    logGroupName=log_group,
    startTime=1646766022, #    int((datetime.today() - timedelta(hours=5)).timestamp()), March 8, 2022 7:00:22 PM
    endTime=1646948926, #int(datetime.now().timestamp()),  March 8, 2022 9:00:31 PM
    queryString=query,
)

query_id = start_query_response['queryId']

response = None

while response == None or response['status'] == 'Running':
    time.sleep(1)
    response = client.get_query_results(
        queryId=query_id
    )

# for elements in response['results']:
#     print("======================================")
#     print(elements)
#     print("======================================")
#     for element in elements:
#         print("------------")
#         print(element['value'])
#         print("------------")


response_json = json.dumps(response, indent=2)

print(response_json)
