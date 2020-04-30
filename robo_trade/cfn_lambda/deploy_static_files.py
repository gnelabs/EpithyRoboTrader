
__author__ = "Nathan Ward"

import os
import zipfile
import logging
from typing import NewType, Any
import boto3
from cfn_lambda.cfnresponse import send, SUCCESS, FAILED

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)
Boto3ResourceType = NewType('Boto3ResourceType', boto3.resource)

def match_content_type(filename: str) -> str:
    """
    Match file extensions to content-type. A quick lightweight list.
    This is needed so s3 vends the right MIME type when the file is downloaded
    directly from the bucket.
    """
    content_type_match = {
        'json': 'application/json',
        'js': 'application/javascript',
        'css': 'text/css',
        'map': 'application/json',
        'svg': 'image/svg+xml',
        'ttf': 'font/ttf',
        'woff': 'font/woff',
        'woff2': 'font/woff2',
        'eot': 'application/vnd.ms-fontobject',
        'txt': 'text/plain',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'ico': 'image/x-icon',
        'html': 'text/html',
        'gif': 'image/gif'
    }
    
    try:
        return content_type_match[filename.rsplit('.', 1)[1]]
    except KeyError:
        return 'application/octet-stream'

def lambda_handler(event, context):
    """
    Lambda function that runs on cloudformation create and update.
    Unzips the website static files build and uploads it to s3.
    """
    current_directory = os.getcwd()
    website_version = os.environ['WEBSITE_VERSION']
    
    _LOGGER.info(
        'Unzipping {cwd}/website_{ver}.zip'.format(
            cwd = current_directory,
            ver = website_version
        )
    )
    
    try:
        zipfile_location = '{cwd}/website_{ver}.zip'.format(
            cwd = current_directory,
            ver = website_version
        )
    except KeyError:
        _LOGGER.error('Missing environment variables for lambda to prepare content.')
        send(event, context, FAILED)
        return
    
    #Unzip. Lambda can only write to /tmp.
    with zipfile.ZipFile(zipfile_location, 'r') as zip_ref:
        zip_ref.extractall('/tmp')
    
    assets_folder = '/tmp/build'

    #Walk the files unzipped to get a full path list of what needs
    #to be uploaded to s3.
    file_list = []
    for root, _, filenames in os.walk(assets_folder):
        for filename in filenames:
            file_list.append(os.path.join(root, filename))
    
    bucket_name = os.environ['S3_STATIC_ASSETS_BUCKET']
    s3_resource = boto3.resource('s3')
    destination_bucket = s3_resource.Bucket(bucket_name)
    
    _LOGGER.info('Cleaning out old items from the bucket.')
    
    #Truncate the bucket (delete all files in it) before uploading.
    try:
        destination_bucket.objects.all().delete()
    except Exception as e:
        _LOGGER.error('Problem truncating bucket. {0}'.format(e))
        send(event, context, FAILED)
        return
    
    _LOGGER.info(
        'Copying static assets version {ver} to S3 bucket {buk}.'.format(
            ver = website_version,
            buk = bucket_name
        )
    )
    
    #Upload.
    for file in file_list:
        try:
            destination_bucket.upload_file(
                Filename = file,
                Key = file.split(assets_folder)[1].strip('/'),
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': match_content_type(file)
                }
            )
        except Exception as e:
            _LOGGER.error('Problem uploading file to s3. {0}'.format(e))
            send(event, context, FAILED)
            return
    
    send(event, context, SUCCESS)
    return