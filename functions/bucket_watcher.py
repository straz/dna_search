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
import traceback
from datetime import datetime
from botocore.exceptions import ClientError

from common import DB_NAME, SQS_ROOT_URL, log_setup

log_setup()


S3 = boto3.client('s3')
SQS = boto3.client('sqs')
DYNAMO = boto3.client('dynamodb')


def lambda_handler(event, context):
    logging.info("event= {}".format(json.dumps(event, indent=2)))
    guid = str(datetime.utcnow())
    env = 'unknown'
    filename = 'unknown'
    email = 'unknown'
    try:
        record = event['Records'][0]
        s3_info = record['s3']
        bucket = s3_info['bucket']['name']
        key = s3_info['object']['key']
        logging.info(f'bucket={bucket}, key={key}')
        metadata = S3.head_object(Bucket=bucket, Key=key)['Metadata']
        logging.info(f'metadata={metadata}')
        guid = metadata['guid']
        email = metadata['email']
        env = metadata['env']
        filename = metadata['filename']
        put_db_item(guid, env, email, filename, 'uploaded')
        new_key = move_file(bucket, key, metadata, env)
        notify_sqs(guid, new_key, env)
    except:
        errmsg = traceback.format_exc()
        put_db_item(guid, env, email, filename, 'error', errmsg)
        raise

def move_file(bucket, old_key, metadata, env):
    old_path = old_key.split('/')
    assert old_path[0] == env
    assert old_path[1] == 'inbox'
    guid = metadata['guid']
    old_file = metadata['filename']
    extension = os.path.splitext(old_file)[1].lower()
    new_key = f'queries/{env}/{guid}{extension}'
    S3.copy({'Bucket': bucket, 'Key': old_key}, bucket, new_key)
    S3.delete_object(Bucket=bucket, Key=old_key)
    logging.info(f'Moved from {old_key}=>{new_key} for guid={guid}')
    return new_key

def notify_sqs(guid, key, env):
    queue_arn = f'{SQS_ROOT_URL}-{env}'
    msg = json.dumps({'guid': guid, 'key': key, 'env': env})
    SQS.send_message(QueueUrl=queue_arn, MessageBody=msg)
    logging.info(f'Sent SQS msg for guid={guid} in env={env}')

def put_db_item(guid, env, email, filename, status, errmsg=None):
    item = {
        "guid": {"S": guid},
        "env": {"S": env},
        "email": {"S": email},
        "filename": {"S": filename},
        "status": {"S": status},
        "start_time": {"S": str(datetime.utcnow())}
        }
    if errmsg:
        item['results'] = { "L" : [ { "M" : { "error" : {"S" : errmsg}}}] }
    DYNAMO.put_item(TableName=DB_NAME, Item=item)
    logging.info(f'Created db entry for guid={guid} in env={env}')
    
