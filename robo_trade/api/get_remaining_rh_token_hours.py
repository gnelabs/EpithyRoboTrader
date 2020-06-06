
__author__ = "Nathan Ward"

import json
from datetime import datetime, timezone
from views import register_view
from api.utils import LambdaMessageEncoder
from trade_lambda.get_credentials import robinhood_creds

@register_view('/api/get_remaining_rh_token_hours')
def lambda_handler(event, context):
    """
    Route that returns the number of hours remaining on the Robinhood
    API auth token. This tells the user whether or not they need to refresh.
    """
    _robinhood_credentials = robinhood_creds()
    expiry = _robinhood_credentials['expiry']
    time_left = expiry - datetime.now(timezone.utc)
    hours_remaining_rounded_down = int(time_left.total_seconds() / 3600)
    
    return {
        'statusCode': 200,
        'body': json.dumps(
            {'remaining_hours': hours_remaining_rounded_down},
            cls=LambdaMessageEncoder
        ),
        'headers': {'Content-Type': 'application/json'}
    }