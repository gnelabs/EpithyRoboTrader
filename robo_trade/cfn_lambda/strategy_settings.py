
__author__ = "Nathan Ward"

import os
import logging
import boto3
from cfn_lambda.cfnresponse import send, SUCCESS, FAILED
from strategies import grid1

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function that runs on cloudformation create.
    It reads through all the strategies to get their schema, and creates
    the settings in the dynamodb table.
    """
    ddb_client = boto3.resource('dynamodb')
    table = ddb_client.Table(os.environ['STRATEGIES_TABLE'])
    
    #To-do: Relative import of strategies modules and loop to insert them all.
    
    try:
        table.put_item(Item = grid1.DEFAULT_SETTINGS)
    except Exception as e:
        _LOGGER.error('Unable stick initial strategy settings into DDB. {0}'.format(e))
        send(event, context, FAILED)
        return
    
    send(event, context, SUCCESS)
    return