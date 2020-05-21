
__author__ = "Nathan Ward"

import logging
import os
from datetime import datetime, timezone
import boto3

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def confirm_enabled(strategy: str) -> bool:
    """
    Grab the global and strategy enabled/disabled setting.
    This controls whether or not trading continues.
    
    Returns True if either global or strategy-based trading is enabled.
    """
    ddb_client = boto3.resource('dynamodb')
    strat_table = ddb_client.Table(os.environ['STRATEGIES_TABLE'])
    globset_table = ddb_client.Table(os.environ['GLOBALSETTINGS_TABLE'])
    
    try:
        global_enabled = globset_table.get_item(Key = {'globalConfig': 'SET'})['Item']['GlobalTradingEnabled']
        strategy_enabled = strat_table.get_item(Key = {'strategyConfig': strategy})['Item']['StrategyTradingEnabled']
    except Exception as e:
        _LOGGER.error('Unable to grab enablement setting DDB values. {0}'.format(e))
        raise Exception('Unable to grab enablement setting DDB values. {0}'.format(e))
    
    if global_enabled == True and strategy_enabled == True:
        return True
    else:
        return False

def check_end_of_day(timestamp: str) -> bool:
    """
    Given an 8601 UTC timestamp, check whether or not the end of trading day is near.
    
    Returns True if the end of trading has been reached.
    """
    market_close = datetime.fromisoformat(timestamp)
    current_time = datetime.now(timezone.utc)
    time_to_close = market_close - current_time
    
    #Five minute buffer to close out any open trades before the market closes.
    if time_to_close.total_seconds() < 300:
        return True
    else:
        return False