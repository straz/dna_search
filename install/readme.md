# Installation

## Dependencies

You must have
 1. Python3
 2. Docker (in order to run AWS SAM local)

## Configure

Configure [settings.py](settings.py)

## Install & Run

Run [start.py](start.py)

## More info

If this is your first time using aws, you'll be prompted for your [aws credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html#cli-quick-configuration)

## Files

### Stuff used during development
`start.py` - main program for starting up a local dev environment
`deploy_lambda.py` - packs up zip for use by SAM
`kill.py` - opposite of `start.py`, good for pesky background jobs
`settings.py` - configuration

### Stuff used to deploy to production
`deploy_lambda.py`

### Stuff you need only once (for each developer)
`start_bootstrap.py` - called by `start.py`, makes sure AWS is properly installed and configured

### Stuff you need only once (for the entire organization)
`build_layer.py` - creates biopython.zip, the deployment package for a lambda layer containing biopython and reference data from NCBI
`ncbi_download.py` - gets reference data from NCBI



