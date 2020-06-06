
__author__ = "Nathan Ward"

import logging
import os
import json
import boto3
from views import register_view
from api.utils import LambdaMessageEncoder

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

@register_view('/api/global_settings')
def lambda_handler(event, context):
    """
    Route that gets and updates global settings depending on type of request.
    """
    try:
        method = event['requestContext']['http']['method']
    except KeyError:
        _LOGGER.error('Unable to extract request type for settings.')
        raise
    
    ddb_client = boto3.resource('dynamodb')
    table = ddb_client.Table(os.environ['GLOBALSETTINGS_TABLE'])
    
    if method == 'GET':
        try:
            global_settings_raw = table.get_item(Key = {'globalConfig': 'SET'})['Item']
        except Exception as e:
            _LOGGER.error('Unable to grab Robinhood DDB values for global settings. {0}'.format(e))
            raise Exception('Unable to grab Robinhood DDB values for global settings. {0}'.format(e))
        
        try:
            global_settings = {
                'GlobalTradingEnabled': global_settings_raw['GlobalTradingEnabled'],
                'ShareResults': global_settings_raw['ShareResults'],
                'ResultsUsername': global_settings_raw['ResultsUsername'],
                'MobileNumber': global_settings_raw['MobileNumber']
            }
        except KeyError:
            _LOGGER.error('Missing global settings key. {0}'.format(e))
            raise
        
        return {
            'statusCode': 200,
            'body': json.dumps(
                global_settings,
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
        
        try:
            table.update_item(
                Key = {'globalConfig': 'SET'},
                UpdateExpression = 'SET {}'.format(','.join(f'#{k}=:{k}' for k in body)),
                ExpressionAttributeValues = {f':{k}': v for k, v in body.items()},
                ExpressionAttributeNames = {f'#{k}': k for k in body}
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
            _LOGGER.error('Unable stick global settings into DDB.')
            return {
                'statusCode': 500,
                'body': json.dumps(
                    {'update_successful': False, 'message': 'Something went wrong server-side.'},
                    cls=LambdaMessageEncoder
                ),
                'headers': {'Content-Type': 'application/json'}
            }
        