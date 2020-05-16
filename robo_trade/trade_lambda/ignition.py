
__author__ = "Nathan Ward"

import logging
import os
import json
import boto3
from trade_lambda.market_hours import get_market_open_close

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def trigger_next_execution(message: dict, delay: int, queue_name: str) -> None:
    sqs = boto3.resource('sqs')
    try:
        queue = sqs.Queue(os.environ[queue_name])
        #Fifo and regular queues act differently.
        if queue_name != 'IGNITION_QUEUE_NAME':
            queue.send_message(
                MessageBody = json.dumps(message),
                MessageGroupId = 'Ignition'
            )
        else:
            queue.send_message(
                MessageBody = json.dumps(message),
                DelaySeconds = delay
            )
    except Exception as e:
        _LOGGER.error('Problem creating ignition message in SQS. {0}'.format(e))
        raise Exception('Problem creating ignition message in SQS. {0}'.format(e))

def lambda_handler(event, context):
    """
    Ignition lambda function. Contains business logic to decide whether or not
    to begin the short-circuit daemon that starts trading.
    """
    market_time_info = get_market_open_close()
    
    #Determine if ignition needs to wait or not.
    if market_time_info['time_now'] < market_time_info['extended_market_open']:
        if market_time_info['extended_time_to_open'] > 900:
            message_delay_seconds = 900
        else:
            message_delay_seconds = int(market_time_info['extended_time_to_open'])
        
        trigger_next_execution(
            message = {
                'message': 'Delaying ignitiong due to market not yet open.',
                'started_extended': False
            },
            delay = message_delay_seconds,
            queue_name = 'IGNITION_QUEUE_NAME'
        )
        return {'message' : 'Delaying ignitiong due to market not yet open.'}  
    else:
        if market_time_info['time_now'] > market_time_info['extended_market_close']:
            return {'message' : 'Market is already closed.'}  
        else:
            if market_time_info['time_now'] < market_time_info['market_open']:
                if market_time_info['time_to_open'] > 900:
                    message_delay_seconds = 900
                else:
                    message_delay_seconds = int(market_time_info['time_to_open'])
                
                if not event['Records'][0]['body']['started_extended']:
                    trigger_next_execution(
                        message = {
                            'message': 'Beginning extended market hours trading.',
                            'begin_trading': True
                        },
                        delay = 0,
                        queue_name = 'EXTENDED_QUEUE_NAME'
                    )
                    _LOGGER.info('Beginning extended market hours trading.')
                
                trigger_next_execution(
                    message = {
                        'message': 'Delaying ignition for regular market hours.',
                        'started_extended': True
                    },
                    groupid = 'Ignition',
                    delay = message_delay_seconds,
                    queue_name = 'IGNITION_QUEUE_NAME'
                )
                return {'message' : 'Delaying ignition for regular market hours.'} 
            else:
                if not event['Records'][0]['body']['started_normal']:
                    trigger_next_execution(
                        message = {
                            'message': 'Beginning normal market hours trading.',
                            'begin_trading': True
                        },
                        delay = 0,
                        queue_name = 'MARKET_QUEUE_NAME'
                    )
                    return {'message' : 'Beginning normal market hours trading.'} 