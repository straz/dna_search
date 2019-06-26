#!/usr/bin/env python3

"""
 Script to deploy lambdas
"""

import os
import boto3
import subprocess
from s3_utils import upload_artifact
from settings import BUILD_DIR, ROOT_DIR, S3_BUCKET, INSTALL_DIR


S3_ZIP_FILE = 'functions.zip'

# hack: AWS template can't reference sibling dirs
BUILD_DIR = INSTALL_DIR
LOCAL_ZIP_PATH  = os.path.join(os.path.abspath(BUILD_DIR), 'functions.zip')

LAMBDA = boto3.client('lambda')

FUNCTIONS = [ 'BucketWatcher', 'GinkgoProcessor', 'GinkgoQueriesGet', 'DevProxy' ]

def deploy(env):
    # Zip package
    zip_cmd = ['zip', '-r9', LOCAL_ZIP_PATH, '.']
    subprocess.call(zip_cmd, cwd=os.path.join(ROOT_DIR, 'functions'))
    if env == 'prd':
        # Upload to S3
        upload_artifact(env, LOCAL_ZIP_PATH, S3_ZIP_FILE)
        # Update functions
        for function in FUNCTIONS:
            key = f'prd/artifacts/{S3_ZIP_FILE}'
            print(f'Updating {function} lambda code')

            LAMBDA.update_function_code(
                FunctionName=function,
                S3Bucket=S3_BUCKET,
                S3Key=key,
                Publish=True
                )

if __name__ == '__main__':
    # This overrides settings.ENV. Use 'prd' to push code to S3 instead of keeping it locally
    deploy('prd')
