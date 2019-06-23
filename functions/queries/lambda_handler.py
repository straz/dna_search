"""
GET /queries/{email}
  body params (form-urlencoded) with: {org, email}
  returns JSON object with: {url, fields, guid}

"""

import logging
import json
import boto3
from boto3.dynamodb.conditions import Key


DYNAMO = boto3.resource('dynamodb')
DB_NAME = 'GinkgoDB'
TABLE = DYNAMO.Table(DB_NAME)

def lambda_handler(event, context):
    email = event['pathParameters']['email']
    response = TABLE.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(email)
        )
    items = json.dumps(response['Items'])
    return {
        "statusCode": 200,
        'body' : f'with_queries({items})'
        }
