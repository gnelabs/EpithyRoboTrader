
__author__ = "Nathan Ward"

import logging
import boto3

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def confirm_enabled(strategy: str) -> bool:
    """
    Grab the global and strategy enabled/disabled setting.
    This controls whether or not trading continues.
    """
    ssm_client = boto3.client('ssm')
    try:
        global_enabled = ssm_client.get_parameter(
            Name = 'EpithyTrader_GlobalTradingEnabled'
        )['Parameter']['Value']
        strategy_enabled = ssm_client.get_parameter(
            Name = 'EpithyTrader_StratEnabled_{0}'.format(strategy)
        )['Parameter']['Value']
    except Exception as e:
        _LOGGER.error('Unable to enablement setting SSM values. {0}'.format(e))
        raise Exception('Unable to enablement setting SSM values. {0}'.format(e))
    
    #SSM only supports strings.
    if global_enabled == 'True' and strategy_enabled == 'True':
        return True
    else:
        return False