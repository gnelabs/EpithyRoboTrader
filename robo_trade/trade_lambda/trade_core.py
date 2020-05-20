
__author__ = "Nathan Ward"

import logging
from trade_lambda.get_credentials import robinhood_creds
from trade_lambda.get_enabled import confirm_enabled, check_end_of_day
from trade_lambda.ledger import write_trade, read_trade
from trade_lambda.messaging import next_execution

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

###################
#   Unifinished   #
###################

def lambda_handler(event, context):
    """
    Core trading lambda. Performs closed-loop trading operations within a trading
    day following a predetermined strategy.
    """
    sqs_message_content = event['Records'][0]['body']
    
    #Log the start of the first run for debugging purposes.
    try:
        if sqs_message_content['begin_trading']:
            _LOGGER.info(sqs_message_content['message'])
    except KeyError:
        pass
    
    #Verify trading is enabled.
    if not confirm_enabled(sqs_message_content['strategy']):
        #Logic to close trades.
        _LOGGER.info('Trading is not enabled. stopping trading.')
        return {'message' : 'Trading is not enabled. stopping trading.'} 
    
    #Verify market close isn't near.
    if check_end_of_day(sqs_message_content['trading_day_end_time']):
        #Logic to close trades.
        _LOGGER.info('The end of day is near, stopping trading.')
        return {'message' : 'The end of day is near, stopping trading.'}
    
    #Robinhood login to execute trades.
    robinhood_credentials = robinhood_creds()
    
    next_execution(
        message = {
            'queue_name': sqs_message_content['queue_name'],
            'trading_day_end_time': sqs_message_content['trading_day_end_time'],
            'strategy': sqs_message_content['strategy'],
            'Testing': True
        },
        queue_name = sqs_message_content['queue_name']
    )