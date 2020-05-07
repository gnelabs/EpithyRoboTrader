
__author__ = "Nathan Ward"

import json
import logging
import boto3
import robin_stocks.helper as helper
import robin_stocks.urls as urls
import robin_stocks
from views import register_view
from api.utils import LambdaMessageEncoder

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

@register_view('/api/get_positions')
def lambda_handler(event, context):
    """
    Lambda function to return the current positions held in the Robinhood account.
    Using this to test functionality of this whole shebang before I go further.
    
    This is a stripped down version of the robin_stocks.authentication.login function.
    Lambda only allows writing to /tmp directory, so the concept of pickling a file into
    the home directory won't work. Using SSM securestring for non-ephemeral replacement
    because its free (to 40 TPS), encrypted, and SSM is backed by dynamodb so its fast.
    """
    #I should probably make this its own function since this will be reused frequently.
    try:
        ssm_client = boto3.client('ssm')
        
        device_token = ssm_client.get_parameter(
            Name = 'EpithyTrader_RH_device_token',
            WithDecryption = True
        )['Parameter']['Value']
        token_type = ssm_client.get_parameter(
            Name = 'EpithyTrader_RH_token_type',
            WithDecryption = True
        )['Parameter']['Value']
        access_token = ssm_client.get_parameter(
            Name = 'EpithyTrader_RH_access_token',
            WithDecryption = True
        )['Parameter']['Value']
        refresh_token = ssm_client.get_parameter(
            Name = 'EpithyTrader_RH_refresh_token',
            WithDecryption = True
        )['Parameter']['Value']
    except Exception:
        _LOGGER.error('Unable to grab Robinhood SSM values.')
        return {
            'statusCode': 500,
            'body': json.dumps(
                {'message': 'Something went wrong server-side.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    
    #Trick robin_stocks into thinking login was successful.
    helper.set_login_state(True)
    
    #Set the JWT.
    helper.update_session('Authorization', '{0} {1}'.format(token_type, access_token))
    
    #Skip verification. Can handle this here if needed.
    result = robin_stocks.account.get_current_positions()
    
    try:
        return {
            'statusCode': 200,
            'body': json.dumps(
                result,
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    except Exception as e:
        _LOGGER.error('Something went wrong querying Robinhood account. {0}'.format(e))
        return {
            'statusCode': 500,
            'body': json.dumps(
                {'message': 'Something went wrong querying Robinhood account. {0}'.format(e)},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }