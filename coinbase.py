import cbpro as coinbase
import csv
import time
from datetime import datetime, timedelta
from typing import Dict

class Product:

    def __init__(self, data: Dict):
        self._data = data

    @property
    def name(self):
        return self._data['id']


class CoinbaseAuth:
    def __init__(self):
        with open('../../.auth/cbpro.txt') as f:
            auth_data = [a.strip() for a in f]
            self.key, self.secret, self.passphrase, self.nickname = auth_data


class BitcoinTrader:

    def __init__(self, auth: CoinbaseAuth, moving_average_days: int = 20):
        self._authenticated_client = coinbase.AuthenticatedClient(
            key=auth.key,
            passphrase=auth.passphrase,
            b64secret=auth.secret)
        self._client = self._authenticated_client

    @property
    def accounts(self) -> Dict:
        return self._authenticated_client.get_accounts()

    @property
    def btc_balance(self) -> float:
        account = next(
            account
            for account in self.accounts
            if account['currency'] == 'BTC')
        return float(account['balance'])

    @property
    def usdc_balance(self) -> float:
        account = next(
            account
            for account in self.accounts
            if account['currency'] == 'USDC')
        return float(account['balance'])

    def is_holding_btc(self) -> Dict:
        balance_btc_in_usdc = self.btc_balance * self.price(self.btc_usdc)
        return balance_btc_in_usdc > self.usdc_balance

    @property
    def products(self) -> Dict:
        return self._client.get_products()

    @property
    def btc_usdc(self) -> Product:
        return next(
            Product(product_data)
            for product_data in self.products
            if product_data['id'] == 'BTC-USDC')

    def tick(self, product: Product):
        return self._client.get_product_ticker(product_id=product.name)

    def price(self, product: Product):
        tick = self._client.get_product_ticker(product_id=product.name)
        return float(tick['price'])

    def buy(self, product: Product):
        price = self.price(product)
        funds = self.usdc_balance
        amount = funds / price
        return self._client.buy(product.name, 'market', size=str(round(amount * 0.98, 7)))

    def sell(self, product: Product):
        amount = self.btc_balance
        return self._client.sell(product.name, 'market', size=str(round(amount * 0.98, 7)))
        # return self._client.place_market_order(product.name, 'sell', size=str(amount * 0.98))

    def __bid(self, product: Product, price, amount):
        self._authenticated_client.cancel_all()
        print(self._authenticated_client.place_limit_order(
            product.name,
            side='buy',
            price=str(round(price, 2)),
            size=str(amount * 0.98)))

    def stop_loss(self, product: Product, price, amount):
        print('Cancelling previous')
        print(self._authenticated_client.cancel_all())
        return self._authenticated_client.place_stop_order(
            product.name,
            stop_type='loss',
            side='sell',
            size=str(round(amount * 0.98, 7)),
            price=str(round(price, 2)))

    def stop_entry(self, product: Product, price, amount):
        print('Cancelling previous')
        print(self._authenticated_client.cancel_all())
        return self._authenticated_client.place_stop_order(
            product.name,
            stop_type='entry',
            side='buy',
            size=str(round(amount * 0.98, 7)),
            price=str(round(price, 2)))


    def __ask(self, product: Product, price, amount):
        self._authenticated_client.cancel_all()
        print(self._authenticated_client.place_limit_order(
            product.name,
            side='sell',
            price=str(round(price, 2)),
            size=str(amount * 0.98)))

    def moving_average(self, product: Product, days=20) -> float:
        all_rates = []
        print('Calculating price')
        for i in range(days):
            start = datetime.now() - timedelta(i+1)
            end = datetime.now() - timedelta(i)
            # Max 1 request per second
            time.sleep(1)
            rates = self._client.get_product_historic_rates(
                product.name,
                granularity=900,
                start=start,
                end=end)
            for rate in rates:
                ms_since_epoch, rate, *_ = rate
                all_rates.append(float(rate))

        print('Calculation finished')
        return sum(all_rates) / len(all_rates)
