import json
import boto3
from datetime import date, timedelta

client = boto3.client('apigateway')

year = 2024
month = 6
start_date = date(year, month, 1)
end_date = date(year, month + 1, 1) - timedelta(days=1)

# print(f"start: {start_date}, end: {end_date}")
key_id = "5wenobr2jg"
page="1"
limit=30

usage_plan_result = client.get_usage(
    usagePlanId="tzxt89",
    keyId=key_id,
    startDate=start_date.isoformat(),
    endDate=end_date.isoformat()
)
usage_plan_result_json = json.dumps(usage_plan_result)
print(usage_plan_result_json)
                                                    
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apigateway/client/get_usage.html