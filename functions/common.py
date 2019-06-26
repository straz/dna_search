import logging

DB_NAME = 'GinkgoDb'
SQS_NAME = 'GinkgoSQS'
SQS_URL = 'https://sqs.us-east-1.amazonaws.com/381450826529/GinkgoSQS'
S3_BUCKET = 'ginkgo-search'

LOG_LEVEL = logging.DEBUG

def log_setup():
    """
    Sets the log level.
    No easy way other than to override AWS Lambda default handlers.
    """
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    logging.basicConfig(format='%(asctime)s %(message)s', level=LOG_LEVEL)


