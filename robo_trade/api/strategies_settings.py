
__author__ = "Nathan Ward"

import logging
import os
import json
import boto3
from views import register_view
from api.utils import LambdaMessageEncoder

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

##################
# In development #
##################

@register_view('/api/strategy_settings')
def lambda_handler(event, context):
    """
    Route that gets and updates strategy settings.
    """
    try:
        method = event['requestContext']['http']['method']
    except KeyError:
        _LOGGER.error('Unable to extract request type for settings.')
        raise
    
    ddb_client = boto3.resource('dynamodb')
    table = ddb_client.Table(os.environ['STRATEGIES_TABLE'])
    
    if method == 'GET':
        try:
            strategy_settings = table.scan()
        except Exception as e:
            _LOGGER.error('Unable to grab Robinhood DDB values for strategy settings. {0}'.format(e))
            raise Exception('Unable to grab Robinhood DDB values for strategy settings. {0}'.format(e))
        
        return {
            'statusCode': 200,
            'body': json.dumps(
                strategy_settings['Items'],
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    elif method == 'POST':
        pass
        #put code here.
        