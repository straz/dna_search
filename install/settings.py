# Settings used during build to load data from NCBI

import os

# User identity for NCBI Entrez
EMAIL = "your@email.com"

INSTALL_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.join(INSTALL_DIR, '..')
BUILD_DIR = os.path.join(ROOT_DIR, 'build')
DATA_DIR = os.path.join(ROOT_DIR, 'layers', 'biopython', 'data')
