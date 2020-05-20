
__author__ = "Nathan Ward"

import json
import logging
import os
import boto3
from robin_stocks.authentication import respond_to_challenge
import robin_stocks.helper as helper
import robin_stocks.urls as urls
from views import register_view
from api.utils import LambdaMessageEncoder

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

@register_view('/api/loginchallenge')
def lambda_handler(event, context):
    """
    Lambda function to generate and cache full Robinhood login details using
    the 2FA code.
    
    This is a stripped down version of the robin_stocks.authentication module.
    """
    try:
        body = json.loads(event['body'])
        code = body['code']
        challenge_id = body['challenge']
        username = body['username']
        password = body['password']
        sendviasms = body['sms']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps(
                {'rh_login_successful': false, 'message': 'No parameters specified or missing parameters.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    
    ddb_client = boto3.resource('dynamodb')
    table = ddb_client.Table(os.environ['CREDENTIALS_TABLE'])
    
    try:
        device_token = table.get_item(Key = {'credsPlatform': 'robinhood'})['Item']['deviceToken']
    except Exception:
        _LOGGER.error('Unable to grab Robinhood device token.')
        return {
            'statusCode': 500,
            'body': json.dumps(
                {'rh_login_successful': false, 'message': 'Something went wrong server-side.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    
    url = urls.login_url()
    
    if sendviasms:
        challenge_type = "sms"
    else:
        challenge_type = "email"
    
    #Client ID appears to be a hardcoded magic number from client requests?
    #Something to watch out for. Could be related to User-Agent & app version.
    payload = {
        'client_id': 'c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS',
        'expires_in': 86400,
        'grant_type': 'password',
        'password': password,
        'scope': 'internal',
        'username': username,
        'challenge_type': challenge_type,
        'device_token': device_token
    }
    
    #Send back the 2FA code to get a challenge ID.
    res = respond_to_challenge(challenge_id, code)
    
    #For code failures.
    if 'challenge' in res:
        return {
            'statusCode': 401,
            'body': json.dumps(
                {'rh_login_successful': false, 'message': 'Failed to login.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    
    #Request to receive the JWT.
    helper.update_session('X-ROBINHOOD-CHALLENGE-RESPONSE-ID', challenge_id)
    data = helper.request_post(url, payload)
    
    if 'access_token' in data:
        try:
            table.put_item(Item = {
                'credsPlatform': 'robinhood',
                'deviceToken': device_token,
                'tokenType': data['token_type'],
                'accessToken': data['access_token'],
                'refreshToken': data['refresh_token']
            })
        except Exception as e:
            _LOGGER.error('Unable stick Robinhood credentials into DDB.')
            return {
                'statusCode': 500,
                'body': json.dumps(
                    {'rh_login_successful': false, 'message': 'Something went wrong server-side.'},
                    cls=LambdaMessageEncoder
                ),
                'headers': {'Content-Type': 'application/json'}
            }
    
    return {
        'statusCode': 200,
        'body': json.dumps(
            {'rh_login_successful': True, 'message': 'Successfully authenticated. Logging in.'},
            cls=LambdaMessageEncoder
        ),
        'headers': {'Content-Type': 'application/json'}
    }