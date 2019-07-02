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

from common import S3_BUCKET, DB_NAME, SQS_URL, log_setup

log_setup()

S3 = boto3.client('s3')
SQS = boto3.client('sqs')
DYNAMO = boto3.client('dynamodb')


def lambda_handler(event, context):
    logging.info("event= {}".format(json.dumps(event)))
    # default value, for error logging
    metadata = {'guid': str(datetime.utcnow())}
    try:
        record = event['Records'][0]
        s3_info = record['s3']
        bucket = s3_info['bucket']['name']
        key = s3_info['object']['key']
        if 'inbox' not in key:
            logging.info(f'ignoring invalid incoming file: bucket={bucket}, key={key}')
            return
        logging.info(f'handling bucket={bucket}, key={key}')
        metadata = S3.head_object(Bucket=bucket, Key=key)['Metadata']
        logging.info(f'metadata={metadata}')
        env = metadata['env']
        filename = metadata['filename']

        if os.environ.get('IS_PRODUCTION', False):
            # Running in production environment.
            if env == 'prd':
                # Ingest upload normally.
                handle_upload_event(bucket, key, metadata)
            else:
                forward_upload_event(bucket, key, env)
        else:
            # Running in local dev environment
            handle_upload_event(bucket, key, metadata)
    except:
        errmsg = traceback.format_exc()
        metadata['errmsg'] = errmsg
        put_db_item(metadata, 'error')
        raise

def forward_upload_event(bucket, key, env):
    """
    Send 'upload' message to dev queue to be handled in dev environment.
    Happens when S3 detects an incoming file (detected by prd) that belongs to dev.
    """
    message = {'dispatch': 'upload',
               'env': env,
               's3' : {'bucket' : {'name': bucket},
                       'object' : {'key': key}}}
    notify_sqs(env, message)

def handle_upload_event(bucket, key, metadata):
    env = metadata['env']
    guid = metadata['guid']
    # Create initial entry
    put_db_item(metadata, 'uploaded')
    # Move from /inbox to /queries
    new_key = move_file(bucket, key, metadata, env)
    # Send 'process' event
    message = {'dispatch' : 'process',
               'env': env,
               'guid': guid,
               'key': new_key
               }
    notify_sqs(env, message)


def move_file(bucket, old_key, metadata, env):
    old_path = old_key.split('/')
    # Validate file is coming from the legit inbox
    assert bucket == S3_BUCKET
    assert old_path[0] == env
    assert old_path[1] == 'inbox'
    guid = metadata['guid']
    old_file = metadata['filename']
    extension = os.path.splitext(old_file)[1].lower()
    new_key = f'{env}/queries/{guid}{extension}'
    S3.copy({'Bucket': bucket, 'Key': old_key}, bucket, new_key)
    S3.delete_object(Bucket=bucket, Key=old_key)
    logging.info(f'Moved from {old_key}=>{new_key} for guid={guid}')
    return new_key

def notify_sqs(env, message):
    """
    :param env: destination environment
    :param message: dict. Should contain either {'dispatch':'upload'} or {'dispatch':'process'}
    """
    queue = f'{SQS_URL}-{env}'
    msg_string = json.dumps(message)
    SQS.send_message(QueueUrl=queue,
                     MessageBody=msg_string)
    logging.info(f'Sent SQS in env={env}: {msg_string}')


def put_db_item(metadata, status):
    env = metadata.get('env', 'unknown')
    guid = metadata.get('guid', 'unknown')
    item = {
        "guid": {"S": guid},
        "env": {"S": env},
        "email": {"S": metadata.get('email', '')},
        "filename": {"S": metadata.get('filename', '')},
        "status": {"S": status},
        "start_time": {"S": str(datetime.utcnow())}
        }
    if status == 'error':
        item['results'] = { "L" : [ { "M" : { "error" : {"S" : metadata.get('errmsg', 'unknown')}}}] }
    DYNAMO.put_item(TableName=DB_NAME, Item=item)
    logging.info(f'Created db entry for guid={guid} in env={env}')
    
