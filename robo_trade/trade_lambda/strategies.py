
__author__ = "Nathan Ward"

import logging
import os
import boto3

def get_strategies() -> list:
    """
    Grab a list of installed trading strategies names.
    """
    ddb_client = boto3.resource('dynamodb')
    table = ddb_client.Table(os.environ['STRATEGIES_TABLE'])
    
    try:
        strategies_list = table.scan(AttributesToGet=['strategyConfig', 'marketHours'])['Items']
        return strategies_list
    except Exception as e:
        _LOGGER.error('Unable to grab list of strategies from DDB. {0}'.format(e))
        raise Exception('Unable to grab list of strategies from DDB. {0}'.format(e))