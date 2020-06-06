
__author__ = "Nathan Ward"

import logging
import os
import json
import boto3
from api.utils import LambdaMessageEncoder

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def next_execution(message: dict, queue_name: str, previous_message: dict, contextid: str) -> None:
    """
    Function to send the next SQS message. Re-used often so its abstracted here.
    
    Standard attributes added to the message:
    queue_name: Template SQS queue name, gets converted to full URL.
    trading_day_end_time: 8601 UTC timestamp representing end-of-day.
    strategy: Strategy name, used to grab settings.
    last_exec_id: Lambda request ID for the previous execution. Gives the message body uniqueness required for deduping.
    """
    sqs = boto3.resource('sqs')
    message['queue_name'] = queue_name
    message['trading_day_end_time'] = previous_message['trading_day_end_time']
    message['strategy'] = previous_message['strategy']
    message['last_exec_id'] = contextid
    
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