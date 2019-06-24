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
import subprocess
from reference_data import main as data_download

from settings import ROOT_DIR, BUILD_DIR


def main():
    print('Building biopython layer')

    # pip install biopython and dependencies into local dir
    pip = ['pip3', 'install', '--target' 'layers/biopython/python', 'biopython']
    subprocess.call(pip, cwd=ROOT_DIR)

    # fetch NCBI data
    data_download()

    pip = ['zip', '-r9', '../biopython.zip', '.']
    subprocess.call(pip, cwd=os.path.join(ROOT_DIR)


if __name__ == '__main__':
    main()

