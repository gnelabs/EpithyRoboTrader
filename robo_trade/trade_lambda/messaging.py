
__author__ = "Nathan Ward"

import logging
import os
import json
import boto3
from api.utils import LambdaMessageEncoder

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def next_execution(message: dict, queue_name: str) -> None:
    """
    Function to send the next SQS message. Re-used often so its abstracted here.
    """
    sqs = boto3.resource('sqs')
    try:
        queue = sqs.Queue(os.environ[queue_name])
        queue.send_message(
            MessageBody = json.dumps(
                message,
                cls=LambdaMessageEncoder
            ),
            MessageGroupId = 'Trading'
        )
    except Exception as e:
        _LOGGER.error('Problem creating next execution with SQS. {0}'.format(e))
        raise Exception('Problem creating next execution with SQS. {0}'.format(e))

def read_message(event: dict) -> dict:
    """
    Convert a lambda event object derived from an SQS message into a usable dict.
    
    All lambdas are set to BatchSize: 1 when reading from SQS.
    """
    try:
        if event['Records'][0]['eventSource'] == 'aws:sqs':
            message_raw = event['Records'][0]['body']
    except KeyError:
        _LOGGER.error('Message is not in a standard SQS format.')
        raise Exception('Message is not in a standard SQS format.')
    
    return json.loads(message_raw)