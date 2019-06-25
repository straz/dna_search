# Settings used during build to load data from NCBI

import os

# User identity for NCBI Entrez
USER_EMAIL = "guest@example.com"

# Developer username
DEV_USERNAME = 'yourname'

# Environment to deploy to. Customize this if you don't want to share your dev environment with others.
ENV = 'prds'

# Local filesystem
INSTALL_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(INSTALL_DIR, '..')
BUILD_DIR = os.path.join(ROOT_DIR, 'build')
DATA_DIR = os.path.join(ROOT_DIR, 'layers', 'biopython', 'data')

DB_NAME = 'GinkoDB'
SQS_ROOT_URL = 'https://sqs.us-east-1.amazonaws.com/381450826529/GinkgoSQS'
S3_BUCKET = 'ginkgo-search'
