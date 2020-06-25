
__author__ = "Nathan Ward"

import logging
import os
import json
import boto3
from views import register_view
from api.utils import LambdaMessageEncoder

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

@register_view('/api/metrics_def')
def lambda_handler(event, context):
    """
    Route that grabs metrics definitions.
    """
    ddb_client = boto3.resource('dynamodb')
    table = ddb_client.Table(os.environ['METRICSDEF_TABLE'])
    
    try:
        metric_def = table.scan()
        return {
        'statusCode': 200,
        'body': json.dumps(
            metric_def['Items'],
            cls=LambdaMessageEncoder
        ),
        'headers': {'Content-Type': 'application/json'}
    }
    except Exception as e:
        _LOGGER.error('Unable to grab metrics definitions from DDB. {0}'.format(e))
        return {
            'statusCode': 500,
            'body': json.dumps(
                {'message': 'Something went wrong server-side.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }