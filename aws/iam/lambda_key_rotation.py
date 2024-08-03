import boto3
from botocore.exceptions import ClientError
import datetime
import json
import os

iam_client = boto3.client('iam')
sns_client = boto3.client('sns')

topic_arn = os.environ["SNS"]

def list_access_key(user, days_filter, status_filter):
    keydetails=iam_client.list_access_keys(UserName=user)
    key_details={}
    user_iam_details=[]
    
    # Some user may have 2 access keys.
    for keys in keydetails['AccessKeyMetadata']:
        if (days:=time_diff(keys['CreateDate'])) >= days_filter and keys['Status']==status_filter:
            key_details['UserName']=keys['UserName']
            key_details['AccessKeyId']=keys['AccessKeyId']
            key_details['days']=days
            key_details['status']=keys['Status']
            user_iam_details.append(key_details)
            key_details={}
    
    return user_iam_details
    
def time_diff(keycreatedtime):
    now=datetime.datetime.now(datetime.timezone.utc)
    diff=now-keycreatedtime
    return diff.days

def create_key(username):
    access_key_metadata = iam_client.create_access_key(UserName=username)
    access_key = access_key_metadata['AccessKey']['AccessKeyId']
    secret_key = access_key_metadata['AccessKey']['SecretAccessKey']
    return access_key,secret_key
    
def disable_key(access_key, username):
    try:
        iam_client.update_access_key(UserName=username, AccessKeyId=access_key, Status="Inactive")
        print(access_key + " has been disabled.")
    except ClientError as e:
        print("The access key with id %s cannot be found" % access_key)
    
def delete_key(access_key, username):
    try:
        iam_client.delete_access_key(UserName=username, AccessKeyId=access_key)
        print (access_key + " has been deleted.")
    except ClientError as e:
        print("The access key with id %s cannot be found" % access_key)
    
def lambda_handler(event, context):
    # details = iam_client.list_users(MaxItems=300)
    # print(details)
    users=[]
    user_iam_details=[]
    text_list=["Following IAM users require replacing their Access Keys as it is older than 45 days :\n"]
    for user in iam_client.list_users()['Users']:
        users.append(user['UserName'])
        print("User: {0}\nUserID: {1}\nARN: {2}\nCreatedOn: {3}\n".format(user['UserName'],user['UserId'],user['Arn'],user['CreateDate']))
    
    for user in users:
        # user_iam_details=list_access_key(user=user,days_filter=90,status_filter='Active')
        user_iam_details=list_access_key(user=user,days_filter=45,status_filter='Active')
        print(user_iam_details)
        
        for _ in user_iam_details:
            text="Username= {}\tAccess Key ID= {}\tDays Active= {}".format(_['UserName'],_['AccessKeyId'],_['days'])
            text_list.append(text+'\n')# To replace the expired key and to create a text message for sns with accessID and SecretID (List to Multiline String)
        
        for _ in user_iam_details:
            disable_key(access_key=_['AccessKeyId'], username=_['UserName'])
            delete_key(access_key=_['AccessKeyId'], username=_['UserName'])
            access_key,secret_key = create_key(username=_['UserName'])
            text=" IAM User = {}  The Access Key = {} Secret Key = {}".format(user,access_key,secret_key)
            text_list.append(text+'\n')
            
    message = ''.join(map(str, text_list))
    print(message)
    sns_client.publish(TopicArn=topic_arn,Message=message)