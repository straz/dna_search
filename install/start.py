#!/usr/bin/env python3

import os
import subprocess
from settings import ROOT_DIR, INSTALL_DIR
from build_layer import main as build_layer

def main():
    #start_sam()
    # Make sure biopython layer is available both locally and on S3.
    build_layer()
    

def start_dynamo():
    """
    Run a local copy of DynamoDB (see https://hub.docker.com/r/amazon/dynamodb-local/)
    Service will be available at http://docker.for.mac.localhost:8000
    """
    check_docker()
    cmd = ['docker', 'run', '-p', '8000:8000', 'amazon/dynamodb-local']
    subprocess.call(cmd, cwd=ROOT_DIR)

def start_sam():
    check_sam()
    cmd = ["sam", "local", "start-api", "--template", "aws-template.yaml"]
    subprocess.call(cmd, cwd=INSTALL_DIR)

def check_sam():
    try:
        subprocess.check_output(["sam", "--help"])
    except:
        print('It looks like you don\'t have AWS SAM installed.')
        exit()        
    check_docker()

def check_docker():
    try:
        subprocess.check_output(["docker", "ps"])
    except:
        print('It looks like docker is not running.', code)
        exit()


if __name__ == "__main__":
    main()
