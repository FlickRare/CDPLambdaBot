from uuid import uuid4
from json import dumps
from coinbase.rest import RESTClient

class Bot:
    def __init__(self,
                 cdp_api_keys,
                 product_id,
                 stack_active,
                 stack_threshold, 
                 stack_quote):
        self.cdp_api_keys = cdp_api_keys
        self.product_id = product_id
        self.stack_active = stack_active
        self.stack_threshold = stack_threshold
        self.stack_quote = stack_quote


    def initialize(self):
        name, privateKey = self.cdp_api_keys["name"], self.cdp_api_keys["privateKey"]
        client = RESTClient(api_key=name, api_secret=privateKey, timeout=1)
        return client


    def available_USDC(self, client):
        trading_pair = self.product_id
        source_ccy = trading_pair.split("-", 1)[1]
        response = client.get_accounts()
        report = response.to_dict()
        for account in report["accounts"]:
            wallet_ccy = account.get("currency")
            if wallet_ccy == source_ccy:
                balance = float(account["available_balance"]["value"])
                return balance

    
    def check_price_drop(self, client):
        product_info = client.get_product(self.product_id)
        current_price = float(product_info.price or 0)
        price_percentage_change = float(product_info.price_percentage_change_24h or 0)
        if price_percentage_change <= self.stack_threshold:
            return True, price_percentage_change
        else:
            return False, current_price, price_percentage_change

    
    def stack_buy_order(self, client):
        order_id = uuid4()
        order = client.market_order_buy(
            client_order_id=str(order_id),
            product_id=self.product_id,
            quote_size=self.stack_quote
        )
        return dumps(order, intent=2)