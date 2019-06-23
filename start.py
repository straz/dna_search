#!/usr/bin/env python3

import os
import subprocess


ROOT_DIR = os.path.dirname(__file__)


def main():
    start_sam()

def start_sam():
    cmd = ["sam", "local", "start-api", "--template", "aws-template.yaml"]
    subprocess.call(cmd, cwd=ROOT_DIR)

def build_biopython_layer():
    cmd = ["build.sh"]
    subprocess.call(cmd, cwd=f'{ROOT_DIR}/layers')


if __name__ == "__main__":
    main()
