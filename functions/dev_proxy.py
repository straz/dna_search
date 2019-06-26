"""
Dev Proxy

Allows local dev environment to pull messages from the dev queue.

GET /{env}/queue
  returns JSONP callback object with list of items
"""

import logging
import json
import boto3
import os
import traceback
from datetime import datetime
from botocore.exceptions import ClientError

from common import SQS_NAME, log_setup

log_setup()

SQS = boto3.resource('sqs')

def lambda_handler(event, context):
    env = event['pathParameters']['env']
    queue = get_queue(env, SQS)
    items = []
    for message in queue.receive_messages(MessageAttributeNames=['*']):
        items.append({'body': message.body, 'attributes': message.attributes})
        message.delete()
    return {
        "statusCode": 200,
        'body' : json.dumps(items)
        }


def get_queue(env, sqs_resource):
    """
    Make sure we have a queue for this environment.
    Create it if it doesn't already exist.
    """
    queue_name = f'{SQS_NAME}-{env}'
    try:
        # Error if it doesn't exist
        return sqs_resource.get_queue_by_name(QueueName=queue_name)
    except:
        queue = sqs_resource.create_queue(QueueName=queue_name)
        logging.warn(f'Created {queue_name}')
        return queue

