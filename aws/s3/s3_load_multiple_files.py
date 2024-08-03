import os
import time
import boto3
import pathlib
import logging
import argparse
from os import path
from datetime import datetime
import multiprocessing
# from multiprocessing import Process

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

boto3.set_stream_logger('boto3.resources',
                        logging.ERROR)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger("botocore").propagate = False

def load_files(json_metadata):
    process = multiprocessing.current_process()
    pid = process.pid
    print("......................................................................................")
    print(f"pid: {pid}, json_metadata: {json_metadata}")
    print("......................................................................................")

def _load_multiple_files_in_filedelivery_database(bucket_name,
                                                  prefix_name):
    starttime = datetime.now()

    json_body = {
        "databaseName": "analytics",
        "owner": "Data_Core",
        "source": "s3",
        "folderName": "analytics_files",
        "jobId": 3,
        "hierarchyId": 6
    }

    s3_client = boto3.client("s3")
    paginator = s3_client.get_paginator("list_objects_v2")

    operation_parameters = {
        'Bucket': bucket_name,
        'Prefix': prefix_name
    }
    response = paginator.paginate(**operation_parameters,
                                  PaginationConfig={"PageSize": 500})
    count = 0
    current_table = ""
    files_by_table_name = []

    for page in response:
        files = page.get("Contents")
        for file in files:
            path = file['Key']
            components = path.split('/')
            if len(components) == 3:
                table_name = components[1]
                if current_table != table_name:
                    if current_table == "":
                        current_table = table_name
                    else:
                        json_body["tables"] = [
                            {
                                "tableName": current_table,
                                "files": files_by_table_name
                            }
                        ]
                        process = multiprocessing.Process(
                            target=load_files,
                            args=(json_body,)
                        )
                        process.start()
                        process.join()
                        files_by_table_name = []
                        current_table = table_name
                # continue grouping files by table_name
                files_by_table_name.append(
                    {
                        "pathS3": "s3://" + bucket_name + "/" + path,
                        "fileSize": file['Size']
                    }
                )
                count += 1
    print(f"Number of files: {count}")

    endtime = datetime.now()
    logger.info("--------------------------------------")
    logger.info(str(endtime))
    elapsed = endtime - starttime
    logger.info("elapsed seconds: " + str(elapsed) + "")
    logger.info("--------------- end -------------------")

    os._exit(os.EX_OK)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", help="bucket name", required=True)
    parser.add_argument("--prefix", help="prefix name", required=True)
    args = parser.parse_args()
    bucket_name = args.bucket
    prefix_name = args.prefix
    _load_multiple_files_in_filedelivery_database(bucket_name,
                                                  prefix_name)

if __name__ == "__main__":
    main()