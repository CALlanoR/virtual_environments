import boto3
import json
from boto3.dynamodb.conditions import Key, Attr

def query(key):
    dynamodb_table = boto3.resource('dynamodb',
                              region_name="us-east-1").Table('DevHealthNexusPatientKeys')

    response = dynamodb_table.query(
        KeyConditionExpression=Key('ENCRYPTED_KEYS').eq(key))
    return response # ['Items'][0]['PATIENTS']


if __name__ == '__main__':
    key = "MhwkwhSWlZEkUMueobhbCypjI1wb7KZ0iH7kgXhsbZ8=,hW+UBaox7hA1DVw1btDFTsPFWgL/XpmvTtJNCeYMjug="
    print(f"key: {key}")
    items = query(key)
    # print(type(items))
    # patients = items['Items'][0]['PATIENTS']
    # print(type(patients))
    # patients_dict = json.loads(patients)
    # print(type(patients_dict))
    # print(items_dict)
    # print(items['PERSON_EDUCATION_DESC'], ":", items['PERSON_HISPANIC_ORIGIN_DESC'])
    print("...........................")
    print(items)
    # print(patients_dict)
    # print(patients_dict['PATIENT_ID'])
    # for item in items:
    #     print(item)
        # print(items['PERSON_EDUCATION_DESC'], ":", item['PERSON_HISPANIC_ORIGIN_DESC'])