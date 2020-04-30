
__author__ = "Nathan Ward"

import decimal
import json


class LambdaMessageEncoder(json.JSONEncoder):
    """
    Custom json encoder to convert nonstandard types.
    This makes it easier to send any old thing back to the client.
    """
    def default(self, obj: any) -> str:
        if not type(obj) in [
            int,
            float,
            complex,
            decimal.Decimal,
            dict,
            tuple,
            list,
            bool
        ] and obj is not None:
            return str(obj)
        
        return json.JSONEncoder.default(self, obj)

