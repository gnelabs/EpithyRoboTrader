
__author__ = "Nathan Ward"

import logging
import os
import boto3

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def robinhood_creds() -> dict:
    """
    Grab Robinhood token information stored in DDB.
    """
    ddb_client = boto3.resource('dynamodb')
    table = ddb_client.Table(os.environ['CREDENTIALS_TABLE'])
    
    try:
        rh_creds = table.get_item(Key = {'credsPlatform': 'robinhood'})['Item']
        return {
            'device_token': rh_creds['deviceToken'],
            'token_type': rh_creds['tokenType'],
            'access_token': rh_creds['accessToken'],
            'refresh_token': rh_creds['refreshToken']
        }
    except Exception:
        _LOGGER.error('Unable to grab Robinhood DDB values.')
        raise