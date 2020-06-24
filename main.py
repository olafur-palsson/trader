from coinbase import BitcoinTrader, CoinbaseAuth
from datetime import datetime

# This one is for most cases
def when_holding_correct_currency(trader: BitcoinTrader, moving_average):
    if trader.is_holding_btc():
        amount_of_btc = trader.btc_balance
        print(f'Stop loss order, {amount_of_btc} @ {moving_average}')
        print(trader.stop_loss(
            product=btc_usdc,
            price=moving_average,
            amount=amount_of_btc))
    else:
        amount_of_usdc = trader.usdc_balance
        amount_to_request = amount_of_usdc / moving_average
        print(f'Stop entry order, {amount_to_request} @ {moving_average}')
        print(trader.stop_entry(
            product=btc_usdc,
            price=moving_average,
            amount=amount_of_usdc / moving_average))



# When we're holding the wrong one we simply trade at market rate.
def when_holding_wrong_currency(trader: BitcoinTrader):
    if trader.is_holding_btc():
        print('Correction sale')
        print(trader.sell(trader.btc_usdc))
    else:
        print('Correction buy')
        print(trader.buy(trader.btc_usdc))

if __name__ == '__main__':
    print('')
    print(f'\t{datetime.now().isoformat()}')
    print('')

    auth = CoinbaseAuth()
    trader = BitcoinTrader(auth)
    btc_usdc = trader.btc_usdc
    moving_average = trader.moving_average(btc_usdc)
    should_be_holding_btc = trader.price(btc_usdc) > moving_average
    is_holding_btc = trader.is_holding_btc()
    is_holding_what_it_should_be_holding = should_be_holding_btc == is_holding_btc

    print(f'Mov av. 20: {moving_average}')
    print(f'Should be h. btc: {should_be_holding_btc}')
    print(f'Is holding: {is_holding_btc}')
    print(f'Is correct: {is_holding_what_it_should_be_holding}')

    if is_holding_what_it_should_be_holding:
        when_holding_correct_currency(trader, moving_average)
    else:
        when_holding_wrong_currency(trader)
