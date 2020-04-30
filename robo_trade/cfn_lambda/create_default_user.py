
__author__ = "Nathan Ward"

import os
import secrets
import string
import logging
import boto3
from cfn_lambda.cfnresponse import send, SUCCESS, FAILED

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function that runs on cloudformation create. Creates a default Cognito user.
    """
    alphabet = string.ascii_letters + string.digits
    password_length = 12
    _password = ''.join(secrets.choice(alphabet) for i in range(password_length))
    default_user_email = 'admin@example.com'
    
    #Verify lambda is running as part of a cloudformation event trigger.
    try:
        _LOGGER.info('Cloudformation event {0}.'.format(event['RequestType']))
    except KeyError:
        _LOGGER.error('Unable to determine cloudformation event type.')
        send(event, context, FAILED)
        return
    
    #Create the user.
    try:
        cognito_client = boto3.client('cognito-idp')
        cognito_response = cognito_client.sign_up(
            ClientId = os.environ['COGNITO_USER_POOL_CLIENT_ID'],
            Username = default_user_email,
            Password = _password,
            UserAttributes = [
                {'Name': 'email', 'Value': default_user_email}
            ]
        )
        _LOGGER.info('Cognito user creation response: {0}.'.format(cognito_response))
        
        #Extract and return the UUID of the user so this can be consumed later on.
        cognito_user_uuid = cognito_response['UserSub']
    except Exception as e:
        _LOGGER.error('Unable to create Cognito default user. {0}'.format(e))
        send(event, context, FAILED)
        return
    
    #Put the password into SSM. Uses default kms key.
    #Overwrite since stack deletion doesn't neccessarily delete the SSM param.
    try:
        ssm_client = boto3.client('ssm')
        ssm_response = ssm_client.put_parameter(
            Name = 'Cognito_admin_user_password',
            Description = 'Password for the default user in Cognito to access the stack manager.',
            Value = _password,
            Type = 'SecureString',
            Overwrite = True
        )
        _LOGGER.info('SSM put parameter response: {0}.'.format(ssm_response))
    except Exception as e:
        _LOGGER.error('Unable stick password into SSM. {0}'.format(e))
        send(event, context, FAILED)
        return
    
    send(event, context, SUCCESS, response_data={'CognitoUserId': cognito_user_uuid})
    return