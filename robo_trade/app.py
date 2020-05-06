
__author__ = "Nathan Ward"

import json
import views

def lambda_handler(event, context):
    """
    Entry point for the serverless website.
    Routes the request to the appropriate view.
    """
    #Normal routes.
    if event['rawPath'] in views.REGISTER:
        return views.REGISTER[event['rawPath']](event, context)
    #Static files in s3.
    elif '/assets/' in event['rawPath'] or '/static/' in event['rawPath']:
        return views.lambda_handler(event, context)
    else:
        return {
           'statusCode': 404,
           'body': json.dumps({'message': 'Not Found.'}),
           'headers': {'Content-Type': 'application/json'}
        }