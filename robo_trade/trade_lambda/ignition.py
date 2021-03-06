
__author__ = "Nathan Ward"

import logging
import os
import json
import boto3
from trade_lambda.market_hours import get_market_open_close
from trade_lambda.strategies import get_strategies
from trade_lambda.rh_lambda_auth import RobinhoodAuth
from trade_lambda.messaging import next_execution

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def trigger_next_execution(message: dict, delay: int, queue_name: str, contextid: str) -> None:
    """
    Function to send the next message. Normal and Fifo have different params.
    """
    sqs = boto3.resource('sqs')
    try:
        queue = sqs.Queue(os.environ[queue_name])
        #Fifo messages can't be delayed arbitrarily, only its preset amount.
        if queue_name != 'IGNITION_QUEUE_NAME':
            next_execution(
                message = message,
                queue_name = queue_name,
                previous_message = {
                    'trading_day_end_time': message['trading_day_end_time'],
                    'strategy': message['strategy']
                },
                contextid = contextid
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
    
    This works by using SQS as a distributed while loop.
    """
    market_time_info = get_market_open_close()
    strategies_list = get_strategies()
    robinhood_auth = RobinhoodAuth()
    rh_login_verified = robinhood_auth.verify_login()
    rh_login_will_expire = robinhood_auth.check_expiry()
    
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
            queue_name = 'IGNITION_QUEUE_NAME',
            contextid = context.aws_request_id
        )
        return {'message' : 'Delaying ignitiong due to market not yet open.'}  
    else:
        if market_time_info['time_now'] > market_time_info['extended_market_close']:
            return {'message' : 'Market is already closed.'}
        elif not rh_login_verified:
            return {'message' : 'Robinhood failed an auth test.'}
        elif rh_login_will_expire:
            return {'message' : 'Robinhood credentials will expire before trading ends.'}
        else:
            if market_time_info['time_now'] < market_time_info['market_open']:
                if market_time_info['time_to_open'] > 900:
                    message_delay_seconds = 900
                else:
                    message_delay_seconds = int(market_time_info['time_to_open'])
                
                try:
                    extended_already_started = event['Records'][0]['body']['started_extended']
                except KeyError:
                    extended_already_started = False
                
                if not extended_already_started:
                    for strategy in strategies_list:
                        if strategy['marketHours'] == 'Extended':
                            trigger_next_execution(
                                message = {
                                    'message': 'Beginning extended market hours trading.',
                                    'begin_trading': True,
                                    'queue_name': 'EXTENDED_QUEUE_NAME',
                                    'strategy': strategy['strategyName'],
                                    'trading_day_end_time': market_time_info['extended_market_close'].isoformat()
                                },
                                delay = 0,
                                queue_name = 'EXTENDED_QUEUE_NAME',
                                contextid = context.aws_request_id
                            )
                            _LOGGER.info('Beginning extended market hours trading.')
                
                trigger_next_execution(
                    message = {
                        'message': 'Delaying ignition for regular market hours.',
                        'started_extended': True
                    },
                    groupid = 'Ignition',
                    delay = message_delay_seconds,
                    queue_name = 'IGNITION_QUEUE_NAME',
                    contextid = context.aws_request_id
                )
                return {'message' : 'Delaying ignition for regular market hours.'} 
            else:
                for strategy in strategies_list:
                    if strategy['marketHours'] == 'Normal':
                        trigger_next_execution(
                            message = {
                                'message': 'Beginning normal market hours trading.',
                                'begin_trading': True,
                                'queue_name': 'MARKET_QUEUE_NAME',
                                'strategy': strategy['strategyName'],
                                'trading_day_end_time': market_time_info['market_close'].isoformat()
                            },
                            delay = 0,
                            queue_name = 'MARKET_QUEUE_NAME',
                            contextid = context.aws_request_id
                        )
                        _LOGGER.info('Beginning normal market hours trading.')
                return {'message' : 'Beginning normal market hours trading.'} 