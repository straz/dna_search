import logging

DB_NAME = 'GinkgoDb'
SQS_ROOT_URL = 'https://sqs.us-east-1.amazonaws.com/381450826529/GinkgoSQS'
S3_BUCKET = 'ginkgo-search'

def log_setup():
    # Override AWS Lambda default logger
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
