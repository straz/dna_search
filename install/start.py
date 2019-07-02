#!/usr/bin/env python3

import os
import re
import sys
import json
import logging
import subprocess
import settings
from kill import kill_web_server
from dev_proxy import main as run_dev_proxy

# Contains stuff that typically only needs to be run once, on initial setup.
import start_bootstrap

logging.basicConfig(level=logging.INFO, format=settings.LOG_FORMAT)


# ----------------------------------------------------
#
# There are three threads running in a dev environment:
#  SAM  - the local docker container hosting the lambdas
#  polling - the proxy that grabs queued dev messages and feeds them to SAM
#  server - a static server, providing the web client
#
# You can trivially break these apart for separate start/stop control,
# but for this exercise we're lumping all three together in a one-click app.
#


def main():
    run_sam()
    run_web_server()
    run_dev_proxy()
    

def run_sam():
    check_sam()
    cmd = ["sam", "local", "start-api"]
    proc = subprocess.Popen(cmd, cwd=settings.INSTALL_DIR)
    logging.info(f'Starting SAM local (pid={proc.pid})')


def check_sam():
    check_docker()
    try:
        subprocess.check_output(["sam", "--help"])
    except:
        print('It looks like you don\'t have AWS SAM installed.')
        exit()        

def check_docker():
    try:
        subprocess.check_output(["docker", "ps"])
    except:
        print('It looks like docker is not running.')
        exit()

def run_web_server(port=8000):
    """
    Serve up static client content at http://localhost:8000
    Fire and forget, this will run in the background
    """
    kill_web_server(port=port)
    update_client_settings()
    cmd = [sys.executable, '-m', 'http.server', '--bind', 'localhost',  '--cgi', f'{port}']
    proc = subprocess.Popen(cmd, cwd=os.path.join(settings.ROOT_DIR, 'client'))
    msg = f"""
    *********
    Now running a local web server (pid={proc.pid}) at http://127.0.0.1:{port}
    To kill this server, run kill.py
    *********
    """
    print(msg)


def update_client_settings():
    """
    Injects ENV and USER_EMAIL (from settings) into the client's static settings.js file,
    so it has the same values when you run it locally.
    """
    api_url = settings.API_URL
    if settings.ENV != 'prd':
        api_url = settings.LOCAL_API_URL
    pattern = re.compile(r'^.*=(.*)$', re.DOTALL)
    path = os.path.join(settings.ROOT_DIR, 'client', 'settings.js')
    with open(path, 'r') as fp:
        contents = fp.read()
    with open(path, 'w') as fp:
        try:
            match = pattern.match(contents)
            if not match:
                raise Exception(f'Could not parse "{path}"')
            client_settings = json.loads(match.group(1))
            client_settings['env'] = settings.ENV
            client_settings['email'] = settings.USER_EMAIL
            client_settings['api_url'] = api_url
            client_settings['upload_url'] = settings.UPLOAD_URL
            if settings.ENV != 'prd':
                client_settings['dev_username'] = settings.DEV_USERNAME
            out = 'const SETTINGS = '
            out += json.dumps(client_settings, indent=2)
            fp.write(out)
        except:
            fp.write(contents)
            raise


if __name__ == "__main__":
    main()
