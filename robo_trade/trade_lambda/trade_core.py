
__author__ = "Nathan Ward"

import logging
from trade_lambda.get_credentials import ssm_robinhood_creds
from trade_lambda.get_enabled import confirm_enabled
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
    pass