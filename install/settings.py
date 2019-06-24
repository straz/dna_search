# Settings used during build to load data from NCBI

import os

# User identity for NCBI Entrez
EMAIL = "your@email.com"

# Developer username
USER = 'yourname'

# Local filesystem
INSTALL_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(INSTALL_DIR, '..')
BUILD_DIR = os.path.join(ROOT_DIR, 'build')
DATA_DIR = os.path.join(ROOT_DIR, 'layers', 'biopython', 'data')

# Developer artifacts (shared)
S3_ARTIFACTS_BUCKET = 'ginkgo-artifacts'

# Personalize this if you don't want to share artifacts
S3_ARTIFACTS_DIR = 'dev'

# 
DEV_SQS_QUEUE = f'GinkoSQS-{USER}'
DEV_S3_BUCKET = f'GinkoS3-{USER}'
DEV_DB = f'GinkoDB-{USER}'
