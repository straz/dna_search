import boto3
from settings import S3_ARTIFACTS_BUCKET, S3_ARTIFACTS_DIR
from botocore.exceptions import ClientError

S3 = boto3.client('s3')


def artifact_exists(s3_filename):
    try:
        S3.head_object(Bucket=S3_ARTIFACTS_BUCKET, Key=f'{S3_ARTIFACTS_DIR}/{s3_filename}')
        return True
    except ClientError:
        # Not found
        return False

def download_artifact(s3_filename, local_filename):
    S3.download_file(S3_ARTIFACTS_BUCKET, f'{S3_ARTIFACTS_DIR}/{s3_filename}', local_filename)

def upload_artifact(local_filename, s3_filename):
    S3.upload_file(local_filename, S3_ARTIFACTS_BUCKET, f'{S3_ARTIFACTS_DIR}/{s3_filename}')
