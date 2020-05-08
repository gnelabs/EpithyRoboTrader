
__author__ = "Nathan Ward"

import logging
from datetime import date, datetime
from pytz import timezone, utc
import boto3

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

def get_market_open_close() -> dict:
    """
    Grab the market open and close settings. Convert timezone.
    Lambdas run in UTC. Settings are set to US/Eastern (NYSE).
    """
    today = date.today()
    date_format = '%H:%M:%S'
    current_time = datetime.now(utc)
    
    ssm_client = boto3.client('ssm')
    try:
        market_open = ssm_client.get_parameter(Name = 'EpithyTrader_MarketOpen')['Parameter']['Value']
        market_close = ssm_client.get_parameter(Name = 'EpithyTrader_MarketClosed')['Parameter']['Value']
    except Exception as e:
        _LOGGER.error('Unable to grab marked open or close from SSM. {0}'.format(e))
        raise Exception('Unable to grab marked open or close from SSM. {0}'.format(e))
    
    market_open_tz = timezone(market_open.rsplit(':', 1)[1])
    market_close_tz = timezone(market_close.rsplit(':', 1)[1])
    
    market_open_datetime = datetime.strptime(market_open.rsplit(':', 1)[0], date_format).time()
    market_close_datetime = datetime.strptime(market_close.rsplit(':', 1)[0], date_format).time()
    
    naive_open_datetime = datetime.combine(today, market_open_datetime)
    naive_close_datetime = datetime.combine(today, market_close_datetime)
    
    open_local_datetime = market_open_tz.localize(naive_open_datetime, is_dst=None)
    close_local_datetime = market_close_tz.localize(naive_close_datetime, is_dst=None)
    
    open_utc_converted_datetime = open_local_datetime.astimezone(utc)
    close_utc_converted_datetime = close_local_datetime.astimezone(utc)
    
    time_to_close = current_time - close_utc_converted_datetime
    
    return {
        'market_open': open_utc_converted_datetime,
        'market_close': close_utc_converted_datetime,
        'time_to_close': time_to_close.total_seconds()
    }