
__author__ = "Nathan Ward"

import os
import logging
import inspect
import boto3
from cfn_lambda.cfnresponse import send, SUCCESS, FAILED

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)


class SettingsDefinition(object):
    """
    Holds configuration for metrics definitions.
    
    Could have been a yaml or something but this was easier.
    
    :param metricName: Name of the metric.
    :type metricName: str
    :param resolution: How often metric is updated. I.e. seconds, hours.
    :type resolution: str
    :param fillGaps: Whether or not to fill missing time series values with a zero.
    :type fillGaps: bool
    :param defaultLookBack: How far to look back for default rendering.
    :type defaultLookBack: int
    :param archived: Whether or not short-term metrics in DDB get archived to S3.
    :type archived: bool
    """
    @staticmethod
    def tradecorerunning() -> dict:
        """
        Metric definition for whether or not the trade core lambda is running.
        
        This tells you on a basic level if the system is operationa. Will probably
        be overwritten in the near future with something more precise, but I
        want to get this working.
        """
        return {
            'metricName': 'TradeCoreRunning',
            'resolution': 'second',
            'fillGaps': True,
            'defaultLookBack': 172800,
            'archived': False,
            'boolMetric': True
        }


def lambda_handler(event, context):
    """
    Lambda function that runs on cloudformation create.
    It populates the metrics definition table with information about
    each metric.
    """
    ddb_client = boto3.resource('dynamodb')
    table = ddb_client.Table(os.environ['METRICSDEF_TABLE'])
    
    metrics_def = SettingsDefinition()
    #This just gets a list of funcs in SettingsDefinition via tuples.
    function_list = inspect.getmembers(metrics_def, predicate=inspect.isfunction)
    
    for item in function_list:
        try:
            table.put_item(Item = item[1]())
        except Exception as e:
            _LOGGER.error('Unable stick metric definition into DDB. {0}'.format(e))
            send(event, context, FAILED)
            return
    
    send(event, context, SUCCESS)
    return