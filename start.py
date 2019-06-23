#!/usr/bin/env python3

import os
import subprocess

ROOT_DIR = os.path.dirname(__file__)

def main():
    start_sam()

def start_sam():
    check_sam()
    cmd = ["sam", "local", "start-api", "--template", "aws-template.yaml"]
    subprocess.call(cmd, cwd=ROOT_DIR)

def check_sam():
    try:
        subprocess.check_output(["sam", "--help"])
    except:
        print('It looks like you don\'t have AWS SAM installed.')
        exit()        
    check_docker()

def check_docker():
    code = subprocess.call(["docker", "ps"])
    if code != 0:
        print('It looks like docker is not running.')
        exit()

def build_biopython_layer():
    cmd = ["build.sh"]
    subprocess.call(cmd, cwd=f'{ROOT_DIR}/layers')

if __name__ == "__main__":
    main()
