
__author__ = "Nathan Ward"

import os
import json
import logging
import boto3
from views import register_view
from api.utils import LambdaMessageEncoder

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

@register_view('/api/checkusercreated')
def lambda_handler(event, context):
    """
    Route that checks if a Cognito user has been created, indicating that
    registration has taken place. Unauthenticated since its queried by /login.
    """
    try:
        cognito_client = boto3.client('cognito-idp')
        cognito_response = cognito_client.describe_user_pool(
            UserPoolId = os.environ['COGNITO_USER_POOL_ID']
        )
        
        num_cognito_users = cognito_response['UserPool']['EstimatedNumberOfUsers']
        
        if num_cognito_users > 0:
            response = {'rh_user_registered': True}
        else:
            response = {'rh_user_registered': False}
    except Exception as e:
        _LOGGER.error('Unable to query Cognito pool info. {0}'.format(e))
        response = {'message': 'Error querying Cognito.'}
    
    return {
        'statusCode': 200,
        'body': json.dumps(
            response,
            cls=LambdaMessageEncoder
        ),
        'headers': {'Content-Type': 'application/json'}
    }