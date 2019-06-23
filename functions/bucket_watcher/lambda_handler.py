"""
BucketWatcher

Watches S3 bucket (ginkgo-search/inbox).
When a file is uploaded to S3:
  enter record in the database
  move file to /queries folder
  send message to SQS


"""

import logging
import json
import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError

# Override AWS Lambda default logger
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)


DB_NAME = 'GinkgoDB'
SQS_NAME = 'https://sqs.us-east-1.amazonaws.com/381450826529/GinkgoSQS'
BUCKET_NAME = 'ginkgo-search'

S3_RESOURCE = boto3.resource('s3')
S3_CLIENT = boto3.client('s3')
DYNAMO_CLIENT = boto3.client('dynamodb')
SQS_CLIENT = boto3.client('sqs')


def lambda_handler(event, context):
    logging.info("event= {}".format(json.dumps(event, indent=2)))
    record = event['Records'][0]
    s3_info = record['s3']
    bucket = s3_info['bucket']['name']
    key = s3_info['object']['key']
    logging.info(f'bucket={bucket}, key={key}')
    metadata = S3_CLIENT.head_object(Bucket=bucket, Key=key)['Metadata']
    logging.info(f'metadata={metadata}')
    guid = metadata['guid']
    email = metadata['email']
    filename = metadata['filename']
    put_db_item(guid, email, filename)
    new_key = move_file(bucket, key, metadata)
    notify_sqs(guid, new_key)


def move_file(bucket, old_key, metadata):
    assert old_key[:6] == 'inbox/'
    guid = metadata['guid']
    old_file = metadata['filename']
    extension = os.path.splitext(old_file)[1]
    new_key = f'queries/{guid}{extension}'
    S3_RESOURCE.Object(bucket, new_key).copy_from(CopySource=f'{bucket}/{old_key}')
    S3_RESOURCE.Object(bucket, old_key).delete()
    logging.info(f'Moved from {old_key}=>{new_key} for guid={guid}')
    return new_key

def notify_sqs(guid, key):
    msg = json.dumps({'guid': guid, 'key': key})
    SQS_CLIENT.send_message(QueueUrl=SQS_NAME, MessageBody=msg)
    logging.info(f'Sent SQS msg for guid={guid}')

def put_db_item(guid, email, filename):
    DYNAMO_CLIENT.put_item(TableName=DB_NAME,
                           Item={
                                 "guid": {"S": guid},
                                 "email": {"S": email},
                                 "filename": {"S": filename},
                                 "status": {"S": 'uploaded'},
                                 "start_time": {"S": str(datetime.utcnow())}
                                 })
    logging.info(f'Created db entry for guid={guid}')
                           

