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
from botocore import UNSIGNED
from botocore.config import Config

logging.basicConfig(level=logging.INFO, format=settings.LOG_FORMAT)

FUNCTIONS = {'upload': 'BucketWatcher',
             'process': 'Processor'}

LAMBDA = boto3.client('lambda',
                      endpoint_url=settings.LOCAL_API_URL,
                      use_ssl=False,
                      verify=False,
                      config=Config(signature_version=UNSIGNED,
                                    retries={'max_attempts': 0}))


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
    logging.info(f'invoke item={item}')
    message = json.loads(item)
    dispatch = message.get('dispatch', 'none')
    function = FUNCTIONS.get(dispatch, None)
    if not function:
        raise Exception(f"Can't handle message: {message}")

    response = LAMBDA.invoke(FunctionName=function,
                             LogType='Tail',
                             Payload=item)
    fmt_response = json.dumps(response, indent=2)
    logging.info(f'response={response}')

if __name__ == '__main__':
    main()
