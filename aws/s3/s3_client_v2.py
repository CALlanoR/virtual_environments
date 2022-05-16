import re
import boto3

def _get_s3_connection():
    return boto3.client("s3")

def get_all_buckets():
    s3_client = _get_s3_connection()
    result = s3_client.list_buckets()
    buckets = [bucket['Name'] for bucket in result['Buckets']]
    return buckets

def delete_all_files_bucket(bucket_name:str,
                            prefix:str,
                            exclude_files_with:str=None):
    s3_client = _get_s3_connection()
    paginator = s3_client.get_paginator('list_objects')
    operation_parameters = {
        'Bucket': bucket_name,
        'Prefix': prefix
    }
    page_iterator = paginator.paginate(**operation_parameters)
    for page in page_iterator:
        print(page['Contents'])
    # args = {
    #     "Bucket": bucket_name,
    #     "Prefix": prefix
    # }
    # result = s3_client.list_objects_v2(**args)
    # count = 0
    # for key in result['Contents']:
    #     if exclude_files_with is not None and exclude_files_with not in key['Key']:
    #         print("++++++++ key: {}".format(key['Key']))
    #         s3_client.delete_object(Bucket=bucket_name,
    #                                 Key=key['Key'])
    #         count+=1

def delete_file_from_bucket(bucket:str,
                            file:str):
    s3_client = _get_s3_connection()
    s3_client.delete_object(Bucket=bucket,
                            Key=file)

def delete_bucket(bucket:str):
    s3_client = _get_s3_connection()
    s3_client.delete_bucket(Bucket=bucket)

def get_s3_path(s3_full_path):
    match = re.match(r"s3://(?P<bucket>(.(?!/))*.)/(?P<path>.*)",
                     s3_full_path).groupdict()
    return match['bucket'], match['path']


# delete_all_files_bucket("healthnexus-athena",
#                         "masterfile/parquet-format/dev")

delete_all_files_bucket("healthnexus",
                        "audience-quality/parameters/")


