
"""
Use at your own risk! The author is not liable for losses incurred.
"""

__author__ = "Nathan Ward"


DESCRIPTION = """
Grid trading strategy using SPY options. Constantly buys and sells, 
while trend-following in certain directions by buying into the grid 
and then selling once a trailing stop-loss is met. Works best during 
volatile markets. Requires free options trading and high-frequency API.

Grid version 1.
Option size: 1
Grid size: 4
"""

DEFAULT_SETTINGS = {
    'strategyName': 'Grid1',
    'marketHours': 'Normal',
    'requiresRobinhood': True,
    'requiresAlpaca': False,
    'requiresTDA': False,
    'requiresRealtime': True,
    'Description': DESCRIPTION,
    'requiresDayTrading': True
}

