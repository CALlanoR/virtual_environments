import boto3
from validate import Validate

class S3Client(object):
    def __init__(self,
                 aws_access_key_id:str,
                 aws_secret_access_key:str,
                 aws_region:str="us-east-1"):
        Validate.not_empty(aws_region,
                           'Region name cannot be null')
        self.client = boto3.client("s3",
                                   region_name=aws_region)

    def get_all_buckets(self):
        result = self.client.list_buckets()
        buckets = [bucket['Name'] for bucket in result['Buckets']]
        return buckets

    def delete_all_files_bucket(self,
                                bucket_name:str,
                                prefix:str) -> bool:
        Validate.not_empty(bucket_name,
                           'Bucket name cannot be null')
        args = {
            "Bucket": bucket_name,
            "Prefix": prefix
        }
        result = self.client.list_objects_v2(**args)
        for key in result['Contents']:
            if int(key['Size'] != 0):
                self.delete_file_from_bucket(bucket_name,
                                             key['Key'])

    def delete_file_from_bucket(self,
                                bucket:str,
                                file:str) -> bool:
        try:
            self.client.delete_object(Bucket=bucket,
                                      Key=file)
            return True
        except Exception as ex:
            print(str(ex))
            return False
        
    def delete_bucket(self,
                      bucket:str):
        self.client.delete_bucket(Bucket=bucket)
