
__author__ = "Nathan Ward"

import os
import logging
import boto3
from cfn_lambda.cfnresponse import send, SUCCESS, FAILED

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function that runs on cloudformation create and update.
    It auto-populates config in the global settings dynamodb table.
    This way settings can be viewed/changed by the frontend.
    """
    ddb_client = boto3.resource('dynamodb')
    table = ddb_client.Table(os.environ['GLOBALSETTINGS_TABLE'])
    
    try:
        table.put_item(Item = {
                'globalConfig': 'SET',
                'GlobalTradingEnabled': False,
                'ShareResults': False,
                'ResultsUsername': '',
                'MobileNumber': ''
            })
    except Exception as e:
        _LOGGER.error('Unable stick initial global settings into DDB.')
        send(event, context, FAILED)
        return
    
    send(event, context, SUCCESS)
    return