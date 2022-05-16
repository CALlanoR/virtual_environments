from s3_client import S3Client

client = S3Client(aws_access_key_id="",
                  aws_secret_access_key="",
                  aws_region="us-east-1")

# print(client.get_all_buckets())

client.delete_all_files_bucket("healthnexus",
                               "athena/masterfile/parquet-format/dev")

