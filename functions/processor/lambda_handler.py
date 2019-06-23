import os
import json
import boto3
import logging
import tempfile
import traceback
from datetime import datetime
from Bio import SeqIO

# Override AWS Lambda default logger
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.DEBUG)


S3 = boto3.client('s3')
BUCKET = 'ginkgo-search'

DYNAMO = boto3.client('dynamodb')
DB_NAME = 'GinkgoDB'

# Data loaded in 'biopython' lambda layer
DATA_DIR = '/opt/data'

def lambda_handler(event, context):
    record = event['Records'][0]
    msg = json.loads(record['body'])
    process_one_file(msg['guid'], msg['key'])

def process_one_file(guid, key):
    """
    Search query sequence for matches.
    Update state of query in dynamodb.
    If matches are found, store results in dynamodb.
    :param guid: query ID
    :param key: S3 file containing query sequence
    """
    logging.info(f'Processing file: {key}')
    try:
        query_seq = read_s3_file(key).seq
        results = []
        for name, reference_seq in REFERENCE_RECORDS.items():
            offset = reference_seq.seq.find(query_seq)
            if offset != -1:
                result = {'filename': name, 'offset': offset}
                results.append(result)
                print(f'found in {name} at {offset}')
        update_database(guid, 'done', results)
        logging.info(f'Update succeeded for guid={guid}')
    except Exception as err:
        report = {'time': str(datetime.utcnow()),
                  'guid': guid,
                  'key': key,
                  'trace' : traceback.format_exc()
                  }
        results = [{'error' : report}]
        update_database(guid, 'error', results)
        raise

def add_result_type_declarations(results):
    """
    Dynamodb requires dict markup declaring the type of every entity
    This marks up the results object.
    """
    return {"L" : 
            [ {"M":
               { k:{"S":str(v)} for k,v in r.items()}
               } for r in results ]
            }

def update_database(guid, status, results):
    """
    :param guid: (string) ID of query to update
    :param status: (string)
    :param results: (list of obj)
    """
    param_results = add_result_type_declarations(results)
    DYNAMO.update_item(
        TableName=DB_NAME,
        Key={'guid': {"S" : guid}, 'email': {"S" : 'guest@example.com'}},
        UpdateExpression="set results = :r, #s=:s",
        ExpressionAttributeValues={ ':r': param_results, ':s': {'S' : status} },
        ExpressionAttributeNames={ '#s': "status"}
        )

def read_reference_data():
    """
    Read sequences local directory (data/) into memory
    Returns dict of {filename: sequence}
    """
    return {f:read_local_file(f) for f in os.listdir(DATA_DIR)}

def read_local_file(filename):
    """
    :param filename: refers to a sequence file in local /data directory
    :return: a sequence (Seq)
    """
    path = os.path.join(DATA_DIR, filename)
    return next(SeqIO.parse(path, 'fasta'))

def read_s3_file(key):
    """
    :param key: refers to a sequence file on S3
    :return: a sequence (Seq)
    """
    path = os.path.join(tempfile._get_default_tempdir(),
                        next(tempfile._get_candidate_names()))
    try:
        S3.download_file(BUCKET, key, path)
        return next(SeqIO.parse(path, 'fasta'))
    finally:
        if os.path.exists(path):
            os.remove(path)

# All data used for queries.
# Keep in memory between lambda calls. TODO: scalability.
REFERENCE_RECORDS = read_reference_data()