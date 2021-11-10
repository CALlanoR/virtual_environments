import awswrangler as wr
ipmort boto3

dynamo = boto3.resource('dynamodb')
table = dynamo.Table('data-services-dev-testing')

sqs = boto3.client('sqs')

def lambda_handler(event, context):
  for record in event['Records']:
    filepaths = record['body'].split(',')
    filepath = filepaths.pop()
    
    #let's you read s3 files directly into memory w/o downloading
    df = wr.pandas.read_parquet(path=filepath).astype(str)
    
    with table.batch_writer() as bw:
      for record in df.to_dict("records"):
        bw.put_item(Item=record)
        
    # create new SQS message if still files to process
    if len(filepaths) > 0:
      new_message = ','.join(file_names)
      sqs.send_message(QueueUrl='url_of_queue', MessageBody=new_message)

      