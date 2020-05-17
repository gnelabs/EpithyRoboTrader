
__author__ = "Nathan Ward"

import logging
import os
import json
import boto3

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
            MessageBody = json.dumps(message),
            MessageGroupId = 'Trading'
        )
    except Exception as e:
        _LOGGER.error('Problem creating next execution with SQS. {0}'.format(e))
        raise Exception('Problem creating next execution with SQS. {0}'.format(e))