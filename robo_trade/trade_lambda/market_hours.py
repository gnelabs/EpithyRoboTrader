
__author__ = "Nathan Ward"

import logging
from datetime import date, datetime
from pytz import timezone, utc

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
    
    #Regular hours
    market_normal_open = '09:30:00'
    market_normal_close = '16:00:00'
    
    #Extended hours for stock
    market_extended_open = '09:00:00'
    market_extended_close = '18:00:00'
    
    #New york timezone for nasdaq/nyse, same timezone as us-east-1
    market_tz = timezone('US/Eastern')
    
    market_open_datetime = datetime.strptime(market_normal_open, date_format).time()
    market_extended_open_datetime = datetime.strptime(market_extended_open, date_format).time()
    market_close_datetime = datetime.strptime(market_normal_close, date_format).time()
    market_extended_close_datetime = datetime.strptime(market_extended_close, date_format).time()
    
    naive_open_datetime = datetime.combine(today, market_open_datetime)
    naive_extended_open_datetime = datetime.combine(today, market_extended_open_datetime)
    naive_close_datetime = datetime.combine(today, market_close_datetime)
    naive_extended_close_datetime = datetime.combine(today, market_extended_close_datetime)
    
    open_local_datetime = market_tz.localize(naive_open_datetime, is_dst=None)
    open_extended_local_datetime = market_tz.localize(naive_extended_open_datetime, is_dst=None)
    close_local_datetime = market_tz.localize(naive_close_datetime, is_dst=None)
    close_extended_local_datetime = market_tz.localize(naive_extended_close_datetime, is_dst=None)
    
    open_utc_converted_datetime = open_local_datetime.astimezone(utc)
    open_extended_utc_converted_datetime = open_extended_local_datetime.astimezone(utc)
    close_utc_converted_datetime = close_local_datetime.astimezone(utc)
    close_extended_utc_converted_datetime = close_extended_local_datetime.astimezone(utc)
    
    time_to_close = current_time - close_utc_converted_datetime
    extended_time_to_close = current_time - close_extended_utc_converted_datetime
    time_to_open = open_utc_converted_datetime - current_time
    extended_time_to_open = open_extended_utc_converted_datetime - current_time
    
    return {
        'market_open': open_utc_converted_datetime,
        'market_close': close_utc_converted_datetime,
        'time_to_close': time_to_close.total_seconds(),
        'time_to_open': time_to_open.total_seconds(),
        'extended_market_open': open_extended_utc_converted_datetime,
        'extended_market_close': close_extended_utc_converted_datetime,
        'extended_time_to_close': extended_time_to_close.total_seconds(),
        'extended_time_to_close': extended_time_to_open.total_seconds()
    }