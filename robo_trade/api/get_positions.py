
__author__ = "Nathan Ward"

import json
import logging
import robin_stocks.helper as helper
import robin_stocks.urls as urls
import robin_stocks
from views import register_view
from api.utils import LambdaMessageEncoder
from trade_lambda.get_credentials import robinhood_creds

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

@register_view('/api/get_positions')
def lambda_handler(event, context):
    """
    Lambda function to return the current positions held in the Robinhood account.
    Using this to test functionality of this whole shebang before I go further.
    
    This is a stripped down version of the robin_stocks.authentication.login function.
    Lambda only allows writing to /tmp directory, so the concept of pickling a file into
    the home directory won't work. Using SSM securestring for non-ephemeral replacement
    because its free (to 40 TPS), encrypted, and SSM is backed by dynamodb so its fast.
    """
    robinhood_credentials = robinhood_creds()
    
    #Trick robin_stocks into thinking login was successful.
    helper.set_login_state(True)
    
    #Set the JWT.
    helper.update_session('Authorization', '{0} {1}'.format(robinhood_credentials['token_type'], robinhood_credentials['access_token']))
    
    #Skip verification. Can handle this here if needed.
    #result = robin_stocks.account.get_current_positions()
    result = robin_stocks.get_name_by_symbol('aapl')
    
    try:
        return {
            'statusCode': 200,
            'body': json.dumps(
                result,
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }
    except Exception as e:
        _LOGGER.error('Something went wrong querying Robinhood account. {0}'.format(e))
        return {
            'statusCode': 500,
            'body': json.dumps(
                {'message': 'Something went wrong querying Robinhood account. {0}'.format(e)},
                cls=LambdaMessageEncoder
            ),
            'headers': {'Content-Type': 'application/json'}
        }