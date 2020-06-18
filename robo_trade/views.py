
__author__ = "Nathan Ward"

import os
import functools
from typing import Callable

#Declare routes available.
REGISTER = {}

def register_view(name: str) -> Callable:
    """
    Decorator to register views. Similar to flask.
    """
    @functools.wraps(name)
    def wrapper(f):
        REGISTER[name] = f
        return f
    return wrapper

def lambda_handler(event, context):
    """
    Static file redirect to s3.
    
    #All objects uploaded are marked as public-read. This gets us direct object URL
    #which gives us a free cert. Beats paying for cloudfront or ACM.
    """
    try:
        location = 'https://{bucket}{path}'.format(
            bucket = os.environ['STATIC_ASSETS_BUCKET'],
            path = event['rawPath']
        )
    except KeyError:
        raise Exception('Missing S3 static website endpoint in env.')
    
    return {
       'statusCode': 301,
       'body': '',
       'headers': {
           'Location': location,
           'Access-Control-Allow-Origin': os.environ['STATIC_ASSETS_BUCKET']
       }
    }

#Relative import of all web (human) lambdas and api lambdas
#Api needs to be imported first, it has utilities web depends on.
from api import *
from web import *

#Client-side routes. Single-page apps that use react browser router
#mimick server-side routes, but don't actually go beyond /. This
#list allows API gateway to succeed the request and kick it back to
#the client react app as part of stackManEnvInfo.currentView. This
#makes it so bookmarks work with API gateway.
client_side_react_views = (
    '/',
    '/login',
    '/register',
    '/settings',
    '/strategies',
    '/systemstatus'
)
for react_view in client_side_react_views:
    REGISTER[react_view] = react_app.lambda_handler