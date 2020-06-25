
__author__ = "Nathan Ward"

import os
import logging
import json
from decimal import Decimal
import boto3

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

class MetricsManager(object):
    def __init__(self) -> None:
        ddb_client = boto3.resource('dynamodb')
        self.table = ddb_client.Table(os.environ['METRICS_TABLE'])
    
    def insert_metric(self, data: dict) -> None:
        """
        Put a metric by inserting data into DDB.
        """
        try:
            self.table.put_item(Item = {
                'metricName': data['metricname'],
                'timeStamp': data['timestamp'],
                'value': Decimal(data['value'])
            })
        except Exception as e:
            _LOGGER.error('Unable to insert metric. {0}'.format(e))
            raise Exception('Unable to insert metric. {0}'.format(e))
    
    def archive(self, data: dict) -> None:
        """
        In development. Will scrape oldest 24 hours of data from
        dynamodb and archive in S3 in a csv format compatible
        with aws athena.
        """
        pass

def lambda_handler(event, context):
    try:
        if event['Records'][0]['eventSource'] == 'aws:sqs':
            message_raw = event['Records'][0]['body']
    except KeyError:
        _LOGGER.error('Message is not in a standard SQS format.')
        raise Exception('Message is not in a standard SQS format.')
    
    body = json.loads(message_raw)
    mm = MetricsManager()
    
    try:
        if body['comptype'] == 'insert':
            mm.insert_metric(body)
        elif body['comptype'] == 'archive':
            mm.archive(body)
    except KeyError:
        _LOGGER.error('Missing comptype to process metrics message.')
        raise Exception('Missing comptype to process metrics message.')