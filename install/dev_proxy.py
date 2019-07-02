#!/usr/bin/env python3

"""
A simple proxy service.
Polls the dev SQS
"""

import os
import time
import json
import requests
import logging
import settings
import boto3
import subprocess

logging.basicConfig(level=logging.INFO, format=settings.LOG_FORMAT)

# Mapping of dispatch key to Lambda function name
FUNCTIONS = {'upload': 'BucketWatcher',
             'process': 'GinkgoProcessor'}


def main():
    url = f'{settings.API_URL}/{settings.ENV}/dev-queue'
    logging.info(f'Started: dev_proxy process (pid={os.getpid()})')
    while True:
        print('.')
        response = requests.get(url)
        logging.info(f'GET {url} => {response})')
        items = response.json()
        if items: 
            logging.info(f'items={items}')
            for item in items:
                invoke_item(item)
        time.sleep(settings.POLL_INTERVAL)


def invoke_item(item):
    """
    :param item: (dict)
    """
    logging.info('*'*100)
    logging.info(f'invoke item={item}')
    logging.info('*'*100)
    body_string = item.get('body', '{}')
    body = json.loads(body_string)
    dispatch = body.get('dispatch', 'none')
    function = FUNCTIONS.get(dispatch, None)
    if not function:
        raise Exception(f"Can't handle message: {item}")
    if dispatch == 'upload':
        # S3 event
        event = {'Records' : [body]}
    else:
        # SQS event
        event = {'Records' : [{'body': body_string}]}
    event_string = json.dumps(event)
    cmd = ['sam', 'local', 'invoke', function]
    response = subprocess.check_output(cmd, input=event_string.encode('utf8'))
    logging.info(f'response={response}')

if __name__ == '__main__':
    main()
