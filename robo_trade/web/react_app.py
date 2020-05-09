
__author__ = "Nathan Ward"

import os
from jinja2 import FileSystemLoader, Environment

def load_html_template(event: dict) -> str:
    """
    Load the html file (generated from the web package) and inject
    info so it can be rendered server-side.
    """
    template_file_name = 'index.html'
    
    templateLoader = FileSystemLoader(searchpath="./")
    templateEnv = Environment(loader=templateLoader)
    template = templateEnv.get_template(template_file_name)
    
    try:
        output = template.render(
            COGNITO_USER_POOL_ID = os.environ['COGNITO_USER_POOL_ID'],
            COGNITO_CLIENT_ID = os.environ['COGNITO_CLIENT_ID'],
            COGNITO_IDENTITY_ID = os.environ['COGNITO_IDENTITY_ID'],
            awsregion = os.environ['AWS_REGION'],
            currentview = event['rawPath']
        )
    except KeyError:
        raise Exception('Missing environment/event variables for lambda to load template.')
    
    return output

def lambda_handler(event, context):
    """
    Root website view. I.e. '/' and client-side routes.
    """
    return {
        'statusCode': 200,
        'body': load_html_template(event),
        'headers': {'Content-Type': 'text/html'}
    }