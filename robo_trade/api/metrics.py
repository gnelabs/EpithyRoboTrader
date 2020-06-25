
__author__ = "Nathan Ward"

import logging
import os
import json
import statistics
import csv
from io import StringIO
from datetime import datetime
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key
from views import register_view
from api.utils import LambdaMessageEncoder

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def fill_gaps(current_time: int, lookback: int, resolution: str) -> set:
    """
    This function will fill time-series gaps. For example, if a second
    resolution metric has no data values for three seconds during a
    period of time, the value will be filled zero.
    
    This helps make the data more palatable for time-series graphs,
    making gaps conspicuous. Easier to do this server-side, gives more flexibility
    to run really simple type of graph libs client side.
    """
    filled_list = []
    
    if resolution == 'second':
        range_amount = 1
    elif resolution == 'minute':
        range_amount = 60
    elif resolution == 'hour':
        range_amount = 3600
    elif resolution == 'day':
        range_amount = 86400
    
    starting_time_epoch  = (current_time - (lookback * range_amount))
    filled_list.extend(range(starting_time_epoch, current_time, range_amount))
    
    return set(filled_list)

def sortbytimestamp(meow: int) -> int:
    """
    Micro function to allow for sorted metrics by timestamp.
    """
    return meow['timeStamp']

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
    
    #Optional row limit (based on time series resolution).
    #Helps render graphs quickly client-side.
    try:
        limit = params['limit']
    except KeyError:
        limit = None
    
    ddb_client = boto3.resource('dynamodb')
    metrics_table = ddb_client.Table(os.environ['METRICS_TABLE'])
    
    try:
        response = metrics_table.query(
            Select = 'SPECIFIC_ATTRIBUTES',
            Limit = int(limit) if limit else 64800,
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
    
    metrics_def_table = ddb_client.Table(os.environ['METRICSDEF_TABLE'])
    
    try:
        metrics_def_result = metrics_def_table.get_item(Key = {'metricName': metricname})['Item']
    except Exception as e:
        _LOGGER.error('Problem getting metrics definition for metric. {0}'.format(e))
        return {
            'statusCode': 500,
            'body': json.dumps(
                {'message': 'Something went wrong server-side.'},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    
    metrics_raw_data = response['Items']
    #I don't intend to store decimals or floats in DDB, although thats how DDB number types
    #get stored when you insert. Convert everything to ints for convienence.
    metrics_data = []
    for item in metrics_raw_data:
        metrics_data.append({key: int(value) for key, value in item.items()})
    
    #Make sure timestamp gaps get filled.
    #Use set comparison since its faster.
    if metrics_def_result['fillGaps']:
        filled_gaps_set = fill_gaps(
            current_time = int(datetime.now().timestamp()),
            lookback = int(metrics_def_result['defaultLookBack']),
            resolution = metrics_def_result['resolution']
        )
        raw_timestamps_from_metrics = set([i['timeStamp'] for i in metrics_data])
        
        missing_timestamps = [x for x in filled_gaps_set if x not in raw_timestamps_from_metrics]
        for item in missing_timestamps:
            metrics_data.append({'timeStamp': item, 'value': 0})
    
    if limit:
        #Limit specified means render recent data, so do
        #not average, provide raw values for the most accuracy.
        #Sort before reading limit.
        metrics_data.sort(key=sortbytimestamp)
        metrics_data_condensed = metrics_data[-int(limit):]
    else:
        #No limit means go back as far as possible in time.
        #To make sure the charts render quickly client-side,
        #Average the values and median the timestamps.
        metrics_data_condensed = []
        chunk_size= 300
        for i in range(0, len(metrics_data), chunk_size):
            chunk = metrics_data[i:i+chunk_size]
            _temptimestamps = []
            _tempvalues = []
            for j in chunk:
                _temptimestamps.append(j['timeStamp'])
                _tempvalues.append(j['value'])
            metrics_data_condensed.append({'timeStamp': statistics.median(map(Decimal, _temptimestamps)), 'value': statistics.mean(_tempvalues)})
        
        #Then sort by timestamp.
        metrics_data_condensed.sort(key=sortbytimestamp)
    
    try:
        keys = metrics_data_condensed[0].keys()
        output = StringIO()
        dict_writer = csv.DictWriter(output, keys)
        dict_writer.writeheader()
        dict_writer.writerows(metrics_data_condensed)
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