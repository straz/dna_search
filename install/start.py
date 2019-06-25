#!/usr/bin/env python3

import os
import re
import sys
import json
import subprocess
from settings import ROOT_DIR, INSTALL_DIR, BUILD_DIR, ENV, USER_EMAIL, DEV_USERNAME

def install_requirements():
    pip_cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']
    subprocess.call(pip_cmd, cwd=INSTALL_DIR)

# bootstrap
#install_requirements()

from build_layer import main as build_layer

AWS_CREDENTIALS = os.path.expanduser('~/.aws/credentials')

def main():
    #check_aws()
    update_client_settings()
    #build_sam()
    # Make sure biopython layer is available both locally and on S3.
    #build_layer()
    #start_sam()

def check_aws():
    """
    If AWS credentials are missing, prompt user for them.
    """
    if not os.path.exists(AWS_CREDENTIALS):
        print('\n'*5)
        print('AWS needs to be configured with your credentials.\n')
        cmd = ['aws', 'configure']
        subprocess.call(cmd, cwd=ROOT_DIR)

def start_dynamo():
    """
    Run a local copy of DynamoDB (see https://hub.docker.com/r/amazon/dynamodb-local/)
    Service will be available at http://docker.for.mac.localhost:8000
    """
    check_docker()
    cmd = ['docker', 'run', '-p', '8000:8000', 'amazon/dynamodb-local']
    subprocess.call(cmd, cwd=ROOT_DIR)

def build_sam():
    #check_sam()
    cmd = ["sam", "build", "-b", BUILD_DIR, "--template", f'{INSTALL_DIR}/aws-template.yaml', '--use-container']
    subprocess.call(cmd, cwd=os.path.join(ROOT_DIR, 'functions'))


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

def update_client_settings():
    """
    Injects ENV and USER_EMAIL (from settings) into the client's static settings.js file,
    so it has the same values when you run it locally.
    """
    pattern = re.compile(r'^.*=(.*)$', re.DOTALL)
    path = os.path.join(ROOT_DIR, 'client', 'settings.js')
    with open(path, 'r') as fp:
        contents = fp.read()
    with open(path, 'w') as fp:
        match = pattern.match(contents)
        if not match:
            raise Exception(f'Could not parse "{path}"')
        client_settings = json.loads(match.group(1))
        client_settings['env'] = ENV
        client_settings['email'] = USER_EMAIL
        if ENV != 'prd':
            client_settings['dev_username'] = DEV_USERNAME
        out = 'const SETTINGS = '
        out += json.dumps(client_settings, indent=2)
        fp.write(out)

if __name__ == "__main__":
    main()
