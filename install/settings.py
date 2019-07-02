# Settings used during build to load data from NCBI

import os

# User identity for NCBI Entrez
USER_EMAIL = "guest@example.com"
AWS_CREDENTIALS = os.path.expanduser('~/.aws/credentials')

# Developer identity for NCBI Entrez
DEV_EMAIL = 'developer@acme.com'
# Developer username
DEV_USERNAME = 'yourname'

# Environment to deploy to. Customize this if you don't want to share your dev environment with others.
ENV = 'dev'

# Local filesystem
INSTALL_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(INSTALL_DIR, '..')
BUILD_DIR = os.path.join(ROOT_DIR, 'build')
DATA_DIR = os.path.join(ROOT_DIR, 'layers', 'biopython', 'data')

DB_NAME = 'GinkoDb'
SQS_NAME = 'GinkgoSQS'
SQS_ROOT_URL = 'https://sqs.us-east-1.amazonaws.com/381450826529/GinkgoSQS'
S3_BUCKET = 'ginkgo-search'
UPLOAD_URL = f'https://{S3_BUCKET}.s3.amazonaws.com'

API_URL = 'https://wxt5vzyewl.execute-api.us-east-1.amazonaws.com/prd'
LOCAL_API_URL = 'http://127.0.0.1:3000'
HTTP_PORT = 8000
POLL_INTERVAL = 3 # poll dev queue every 3 seconds

# When running start.py, first you 'pip install' amazon libraries
# This is noisy and slow, so you can turn it off after the first time.
SKIP_PIP = True
LOG_FORMAT = '[%(asctime)s] %(message)s'
