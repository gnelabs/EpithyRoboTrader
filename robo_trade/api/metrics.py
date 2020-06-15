
__author__ = "Nathan Ward"

import logging
import os
import json
import csv
from io import StringIO
import boto3
from boto3.dynamodb.conditions import Key
from views import register_view
from api.utils import LambdaMessageEncoder

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

@register_view('/api/metrics')
def lambda_handler(event, context):
    """
    Route that grabs metrics from ddb based on metric name param.
    """
    try:
        params = event['queryStringParameters']
        metricname = params['name']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps(
                {'message': 'Metric name not specified.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    
    #Optional row limit (based on time series resolution). May use in the future.
    try:
        limit = params['limit']
    except KeyError:
        limit = None
    
    ddb_client = boto3.resource('dynamodb')
    table = ddb_client.Table(os.environ['METRICS_TABLE'])
    
    try:
        response = table.query(
            Select = 'SPECIFIC_ATTRIBUTES',
            Limit = limit if limit else 64800,
            ProjectionExpression = '#t, #v',
            ExpressionAttributeNames = {'#t': 'timeStamp', '#v': 'value'},
            KeyConditionExpression = Key('metricName').eq(metricname),
            #Will grab results in descending order by date.
            ScanIndexForward = False,
            ConsistentRead = False
        )
    except Exception as e:
        _LOGGER.error('Problem querying dynamodb for metrics. {0}'.format(e))
        return {
            'statusCode': 500,
            'body': json.dumps(
                {'message': 'Something went wrong server-side.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    
    try:
        items = response['Items']
        items.reverse()
        keys = items[0].keys()
        output = StringIO()
        dict_writer = csv.DictWriter(output, keys)
        dict_writer.writeheader()
        dict_writer.writerows(items)
        return {
            'statusCode': 200,
            'body': output.getvalue(),
            'headers': {'Content-Type': 'text/csv'}
        }
    except Exception as e:
        _LOGGER.error('Problem converting data to csv. {0}'.format(e))
        return {
            'statusCode': 500,
            'body': json.dumps(
                {'message': 'Something went wrong server-side.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }