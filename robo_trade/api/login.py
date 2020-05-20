
__author__ = "Nathan Ward"

import json
import logging
import os
import boto3
from robin_stocks.authentication import generate_device_token
import robin_stocks.urls as urls
import robin_stocks.helper as helper
from views import register_view
from api.utils import LambdaMessageEncoder

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def generate_challenge(user: str, passwd: str, device_token: str, sendviasms: bool) -> str:
    """
    Generate a 2FA challenge ID by logging into Robinhood with the user/pass.
    
    This is a stripped down version of the robin_stocks.authentication module.
    """
    if sendviasms:
        challenge_type = "sms"
    else:
        challenge_type = "email"
    
    url = urls.login_url()
    
    #Client ID appears to be a hardcoded magic number from client requests?
    #Something to watch out for. Could be related to User-Agent & app version.
    payload = {
        'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
        'expires_in': 86400,
        'grant_type': 'password',
        'password': passwd,
        'scope': 'internal',
        'username': user,
        'challenge_type': challenge_type,
        'device_token': device_token
    }
    
    #Initial query to create a challenge request.
    data = helper.request_post(url, payload)
    
    try:
        return data['challenge']['id']
    except KeyError:
        return ""

@register_view('/api/login')
def lambda_handler(event, context):
    """
    Lambda function to receive credentials for Robinhood login and generate
    a 2FA code for the user to input. Currently only supports challenge 
    2FA requests, and not MFA.
    """
    try:
        body = json.loads(event['body'])
        username = body['username']
        password = body['password']
        sendviasms = body['sms']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps(
                {'challenge_id': '', 'message': 'No parameters specified or missing parameters.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    
    device_token = generate_device_token()
    
    try:
        ddb_client = boto3.resource('dynamodb')
        table = ddb_client.Table(os.environ['CREDENTIALS_TABLE'])
        table.put_item(Item = {
            'credsPlatform': 'robinhood',
            'deviceToken': device_token
        })
    except Exception:
        _LOGGER.error('Unable stick Robinhood device token into DDB.')
        return {
            'statusCode': 500,
            'body': json.dumps(
                {'challenge_id': '', 'message': 'Something went wrong server-side.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    
    challenge_id = generate_challenge(
        user = username,
        passwd = password,
        device_token = device_token,
        sendviasms = sendviasms
    )
    if challenge_id:
        return {
            'statusCode': 200,
            'body': json.dumps(
                {'challenge_id': challenge_id, 'message': 'Successfully generated challenge ID.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    else:
        return {
            'statusCode': 401,
            'body': json.dumps(
                {'challenge_id': '', 'message': 'Failed to login.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }