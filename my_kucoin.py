import json
import os
import threading
import config
from kucoin.client import Client

class Mykucoin():
    def __init__(self, live):
        if live == 1:
            self.client = Client(config.API_KEY, config.API_SECURET, config.API_PASSWORD)
            self.apiKey = config.API_KEY
            self.secret = config.API_SECURET
            self.password = config.API_PASSWORD
        else:
            self.apiKey = config.DEMO_API_KEY
            self.secret = config.DEMO_API_SECURET
            self.password = config.DEMO_API_PASSWORD

    def get_ticker(self):
        # threading.Timer(3000.0, printit).start()
        pull = self.client.get_ticker()
        coinType = pull['ticker'][0]["buy"]
        buyPrice = pull['ticker'][0]["sell"]

        # return pull['ticker'][0]
        return format(coinType), format(buyPrice)

    def get_orders(self):
        result = self.client.get_orders()
        return result