
__author__ = "Nathan Ward"

import os
import socket
import json
import requests
from views import register_view
from api.utils import LambdaMessageEncoder

@register_view('/api/debug')
def lambda_handler(event, context):
    """
    Route that provides json dump about the execution. Used for debugging.
    Authenticated with cognito, since it vends credentials in the output.
    """
    try:
        external_ip = requests.get('https://api.ipify.org').text
    except Exception as e:
        raise Exception('Unable to aquire external IP. {0}').format(e)
    
    net_info = {
        'hostname': socket.gethostname(),
        'internal_ip': socket.gethostbyname(socket.gethostname()),
        'external_ip': external_ip
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(
            {
                'event_raw': event,
                'context_raw': context.__dict__,
                'cwd': os.listdir(os.getcwd()),
                'env_vars': dict(os.environ),
                'network': net_info
            },
            cls=LambdaMessageEncoder
        ),
        'headers': {'Content-Type': 'application/json'}
    }