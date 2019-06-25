import boto3
from settings import S3_BUCKET
from botocore.exceptions import ClientError

S3 = boto3.client('s3')


def artifact_exists(env, s3_filename):
    try:
        key = f'{env}/artifacts/{s3_filename}'
        S3.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except ClientError:
        # Not found
        return False

def download_artifact(env, s3_filename, local_filename):
    key = f'{env}/artifacts/{s3_filename}'
    S3.download_file(S3_BUCKET, key, local_filename)

def upload_artifact(env, local_filename, s3_filename):
    key = f'{env}/artifacts/{s3_filename}'
    S3.upload_file(local_filename, S3_BUCKET, key)
