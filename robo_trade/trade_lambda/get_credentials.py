
__author__ = "Nathan Ward"

import logging
import boto3

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def ssm_robinhood_creds() -> dict:
    """
    Grab Robinhood token information stored in SSM.
    """
    ssm_client = boto3.client('ssm')
    try:
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
        raise
    
    return {
        'device_token': device_token,
        'token_type': token_type,
        'access_token': access_token,
        'refresh_token': refresh_token
    }