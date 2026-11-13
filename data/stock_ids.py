"""Single place for every stock ID used by the automation.

Update the values in ``STOCK_IDS`` when test vehicles change. Tests and page
objects must import these values through ``config.py`` instead of hardcoding a
stock ID elsewhere.
"""


STOCK_IDS = {
    "auction_calculator": "SAT-19695181",
    "non_stolen_vehicle": "SAT-58989252",
    "invalid": "INVALID-ID-12345",
}
