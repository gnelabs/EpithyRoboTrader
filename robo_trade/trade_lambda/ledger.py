
__author__ = "Nathan Ward"

import logging
import os
import boto3

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

###################
#   Unifinished   #
###################

def write_trade() -> None:
    """
    Create or update a record in dynamodb to manage the state of the trade.
    """
    client = boto3.resource('dynamodb')
    ddb_table = client.Table(os.environ['TRADE_ACTIVITY_TABLE'])
    try:
        ddb_table.put_item(Item = data_to_insert)
    except Exception as e:
        _LOGGER.error('Problem updating dynamodb trade data. {0}'.format(e))
        raise Exception('Problem updating dynamodb trade data. {0}'.format(e))