"""
GET /{env}/queries/{email}
  body params (form-urlencoded) with: {org, email}
  returns JSONP callback object with list of items
"""

import logging
import json
import boto3
from boto3.dynamodb.conditions import Key

from common import DB_NAME

DYNAMO = boto3.resource('dynamodb')
TABLE = DYNAMO.Table(DB_NAME)

def lambda_handler(event, context):
    jsonp_callback = 'with_queries' # name of client-side js function
    env = event['pathParameters']['env']
    email = event['pathParameters']['email']
    response = TABLE.query(
        IndexName='env-email-index',
        KeyConditionExpression=Key('env').eq(env) & Key('email').eq(email))
    items = json.dumps(response['Items'])
    return {
        "statusCode": 200,
        'body' : f'{jsonp_callback}({items})'
        }
