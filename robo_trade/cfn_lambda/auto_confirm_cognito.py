
__author__ = "Nathan Ward"

def lambda_handler(event, context):
    """
    Lambda function that verifies a Cognito user creation automatically.
    """
    event['response']['autoConfirmUser'] = True
    
    if 'email' in event['request']['userAttributes']:
        event['response']['autoVerifyEmail'] = True
    
    if 'phone_number' in event['request']['userAttributes']:
        event['response']['autoVerifyPhone'] = True
    
    return event