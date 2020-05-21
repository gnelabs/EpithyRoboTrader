
__author__ = "Nathan Ward"

import logging
from datetime import datetime, timezone
import robin_stocks.helper as helper
import robin_stocks
from trade_lambda.get_credentials import robinhood_creds

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)


class RobinhoodAuth(object):
    def __init__(self):
        """
        The constructor will download credentials stored in DDB and
        set robin_stocks to a logged-in state.
        """
        _robinhood_credentials = robinhood_creds()
        self.expiry = _robinhood_credentials['expiry']
        
        #Trick robin_stocks into thinking login was successful.
        helper.set_login_state(True)
        
        #Set the JWT.
        helper.update_session(
            'Authorization', '{0} {1}'.format(
                _robinhood_credentials['token_type'],
                _robinhood_credentials['access_token']
            )
        )
    
    def verify_login(self) -> bool:
        """
        Verify robinhood can login by performing a basic query.
        
        Returns True if it can.
        """
        result = robin_stocks.get_name_by_symbol('aapl')
        
        if result == 'Apple':
            return True
        else:
            return False
    
    def check_expiry(self) -> bool:
        """
        Checks if expiry is less than nine hours away (start of an extended trading day).
        
        Returns True if it is less, meaning credentials need to be refreshed.
        """
        time_left = self.expiry - datetime.now(timezone.utc)
        
        if time_left.total_seconds() < 32400:
            return True
        else:
            return False