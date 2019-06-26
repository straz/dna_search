#!/usr/bin/env python3

"""
Kills the simple static web server (typically running in background)

Implementation: kills any Python job listening on port 8000
Tested on MacOS only.
"""

import logging
import subprocess
import settings

logging.basicConfig(level=logging.INFO, format=settings.LOG_FORMAT)


def kill_sam_local():
    # ps -e | grep "sam local start-api" | grep Python | awk '{print $1}'
    c1 = ['ps', '-e']
    c2 = ['grep', 'sam local start-api']
    c3 = ['grep', 'Python']
    c4 = ['awk', '{print $1}']
    ps1 = subprocess.Popen(c1, stdout=subprocess.PIPE)
    ps2 = subprocess.Popen(c2, stdout=subprocess.PIPE, stdin=ps1.stdout)
    ps3 = subprocess.Popen(c3, stdout=subprocess.PIPE, stdin=ps2.stdout)
    pid = subprocess.check_output(c4, stdin=ps3.stdout).decode('ascii').strip()
    ps1.wait()
    if pid:
        subprocess.call(['kill', pid])
        logging.info(f'killed SAM local (pid={pid})')
    
def kill_web_server(port=settings.HTTP_PORT):
    c1 = ['lsof', '-iTCP', '-sTCP:LISTEN', '-n', '-P']
    c2 = ['grep', str(port)]
    c3 = ['grep', 'Python']
    c4 = ['awk', '{print $2 ;}']
    ps1 = subprocess.Popen(c1, stdout=subprocess.PIPE)
    ps2 = subprocess.Popen(c2, stdout=subprocess.PIPE, stdin=ps1.stdout)
    ps3 = subprocess.Popen(c3, stdout=subprocess.PIPE, stdin=ps2.stdout)
    pid = subprocess.check_output(c4, stdin=ps3.stdout).decode('ascii').strip()
    ps1.wait()
    if pid:
        subprocess.call(['kill', pid])
        logging.info(f'killed web server (pid={pid})')


if __name__ == '__main__':
    kill_web_server()
    kill_sam_local()
