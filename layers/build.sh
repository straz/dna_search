#!/bin/bash

# Script to build the 'biopython' lambda layer.
# Contains:
#     biopython (python library)
#     dependences (numpy)
#     data: reference files from NCBI
# This builds a zipfile suitable for uploading

echo 'Building biopython layer'
ROOT=`basename ${0%/*}`

pip3 install --target ${ROOT}/biopython/python biopython

# fetch NCBI data
${ROOT}/fetch.py

cd ${ROOT}/biopython

zip -r9 ../biopython.zip .
