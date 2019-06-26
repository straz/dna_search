"""
Stuff that typically only needs to be executed once, on first setup.
This is invoked by start.py

"""
import os
import sys
import settings


def install_requirements():
    pip_cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']
    subprocess.call(pip_cmd, cwd=settings.INSTALL_DIR)
    

def check_aws():
    """
    If AWS credentials are missing, prompt user for them.
    """
    if not os.path.exists(settings.AWS_CREDENTIALS):
        print('\n'*5)
        print('AWS needs to be configured with your credentials.\n')
        cmd = ['aws', 'configure']
        subprocess.call(cmd, cwd=ROOT_DIR)



# Go ahead and install them now.
if not settings.SKIP_PIP:
    # pip install amazon libraries
    # This is noisy and slow, so you can turn it off after the first time.
    install_requirements()

# Also, you probably only need this once.
check_aws()

