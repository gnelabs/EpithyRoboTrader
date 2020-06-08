
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
        try:
            body = json.loads(event['body'])
        except KeyError:
            return {
                'statusCode': 400,
                'body': json.dumps(
                    {'update_successful': False, 'message': 'No parameters specified or missing parameters.'},
                    cls=LambdaMessageEncoder
                ),
                'headers': {'Content-Type': 'application/json'}
            }
        
        #Settings changes come in the form of a simple key:value where
        #the name of the key infers the setting type, and the value is
        #the change. E.g. '{"Grid1_paper": false}'
        body_split = list(body.keys())[0].split('_')
        strat_name = body_split[0]
        if 'paper' in body_split[1]:
            strat_change = 'paperTrading'
        elif 'enable' in body_split[1]:
            strat_change = 'enabled'
        setting = list(body.values())[0]
        
        try:
            table.update_item(
                Key = {'strategyName': strat_name},
                UpdateExpression = 'SET {0} = :a'.format(strat_change),
                ExpressionAttributeValues = {':a': setting}
            )
            return {
                'statusCode': 200,
                'body': json.dumps(
                    {'update_successful': True, 'message': 'Update successful.'},
                    cls=LambdaMessageEncoder
                ),
                'headers': {'Content-Type': 'application/json'}
            }
        except Exception as e:
            _LOGGER.error('Unable stick strategy setting into DDB. {0}'.format(e))
            return {
                'statusCode': 500,
                'body': json.dumps(
                    {'update_successful': False, 'message': 'Something went wrong server-side.'},
                    cls=LambdaMessageEncoder
                ),
                'headers': {'Content-Type': 'application/json'}
            }
        