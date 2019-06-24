#!/usr/bin/env python3

"""
 Script to build the 'biopython' lambda layer.
 Contains:
     biopython (python library)
     dependences (numpy)
     data: reference files from NCBI
 This builds a zipfile suitable for uploading

 Output file: build/biopython.zip
"""

import os
from sys import platform
import subprocess

from ncbi_download import main as ncbi_download
from settings import ROOT_DIR, BUILD_DIR
from s3_utils import artifact_exists, upload_artifact, download_artifact

S3_ZIP_FILE = 'biopython.zip'
LOCAL_ZIP_PATH  = os.path.join(os.path.abspath(BUILD_DIR), 'biopython.zip')

platform_warning = \
f"""
********************************
biopython layer should be created on a linux platform
This layer may not work properly (platform='{platform}')
********************************
"""

def main():
    """
    Attempt to ensure copies of biopython.zip is available both locally and on S3.
    If either one is missing, syncronize it.
    If both are missing, build a new one and upload it.

    Artifacts on S3 live in the S3_ARTIFACTS_DIR, which can be configured in settings.py
    """
    s3_exists = artifact_exists(S3_ZIP_FILE)
    local_exists = os.path.exists(LOCAL_ZIP_PATH)

    if s3_exists and local_exists:
        return

    if s3_exists and not local_exists:
        print('Biopython layer exists on S3, downloading local copy.')
        download_artifact(S3_ZIP_FILE, LOCAL_ZIP_PATH)
        return

    if not s3_exists and local_exists:
        print('Local biopython layer exists, uploading to S3.')
        upload_artifact(LOCAL_ZIP_PATH, S3_ZIP_FILE)
        return

    print('Building biopython layer')
    if platform != 'linux':
        print(platform_warning)
        if not yes_or_no('Proceed?'):
            exit()
        
    # Build local zip file

    # pip install biopython and dependencies into local dir
    pip_cmd = ['pip3', 'install', '--target', 'layers/biopython/python', 'biopython']
    subprocess.call(pip_cmd, cwd=ROOT_DIR)

    # fetch NCBI data
    ncbi_download()

    zip_cmd = ['zip', '-r9', LOCAL_ZIP_PATH, '.']
    subprocess.call(zip_cmd, cwd=os.path.join(ROOT_DIR, 'layers', 'biopython'))

    # Push up to S3
    upload_artifact(LOCAL_ZIP_PATH, S3_ZIP_FILE)

def yes_or_no(question):
    """
    Ask a question, get a boolean.
    Default is No/False
    """
    reply = str(input(question+' (y/N): ')).lower().strip()
    if not reply or reply[0] == 'n':
        return False
    if reply[0] == 'y':
        return True
    else:
        return yes_or_no("Uhhhh... please enter ")

if __name__ == '__main__':
    main()
