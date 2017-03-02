import json                                                                                                                                                                                                         
import csv
import shelve
import time
import datetime
import dateutil.parser

from Robinhood import Robinhood

def get_symbol_from_instrument_url(rb_client, url, db):
    instrument = {}
    if url in db:
        instrument = db[url]
    else:
        db[url] = fetch_json_by_url(rb_client, url)
        instrument = db[url]
    return instrument['symbol']


def fetch_json_by_url(rb_client, url):
    return rb_client.session.get(url).json()


def order_item_info(order, rb_client, db):
    #side: .side,  price: .average_price, shares: .cumulative_quantity, instrument: .instrument, date : .last_transaction_at
    symbol = get_symbol_from_instrument_url(rb_client, order['instrument'], db)
    return {
        'side': order['side'],
        'price': order['average_price'],
        'shares': order['cumulative_quantity'],
        'symbol': symbol,
        'date': order['last_transaction_at'],
        'state': order['state']
    }


def get_all_history_orders(rb_client):
    orders = []
    past_orders = rb.order_history()
    orders.extend(past_orders['results'])
    while past_orders['next']:
        print("{} order fetched".format(len(orders)))
        next_url = past_orders['next']
        past_orders = fetch_json_by_url(rb_client, next_url)
        orders.extend(past_orders['results'])
    print("{} order fetched".format(len(orders)))
    return orders

def get_first_page(rb_client):
    orders = rb.order_history()
    return orders

def get_next_history_page(rb_client, next_url):
    return fetch_json_by_url(rb_client, next_url);


rb = Robinhood()
rb.login_prompt();
instruments_db = {}

past_orders = get_all_history_orders(rb)
orders = [order_item_info(order, rb, instruments_db) for order in past_orders]

while True:
    ticker = raw_input('Which stock ticker?: ').upper()

    sells = []
    sell_count = 0

    buys = []
    buy_count = 0

    for order in orders:
        order_date = dateutil.parser.parse(order['date']).replace(tzinfo=None)

        if float(order['shares']) > 0 and order['symbol'] == ticker:
            if order['side'] == 'sell':
                sells.append(order)
                sell_count = sell_count + float(order['shares'])
            else:
                buys.append(order)
                buy_count = buy_count + float(order['shares'])
            
    total_buy = 0
    shares_traded = 0
    total_sell = 0

    print "======"
    print "BOUGHT"
    print "======"
    for buy in buys:
        price = float(buy['price']) * float(buy['shares'])
        print "{} : #{} @ ${} .. ${}".format(buy['symbol'], buy['shares'], buy['price'], price)
        total_buy = total_buy + price
    print "======"
    print "SOLD"
    print "======"
    for sell in sells:
        price = float(sell['price']) * float(sell['shares'])
        print "{} : #{} @ ${} .. ${}".format(sell['symbol'], sell['shares'], sell['price'], price)
        total_sell = total_sell + price
        shares_traded = shares_traded + float(sell['shares'])

    print "total value moved: ${}".format(total_sell + total_buy)
    print "total winnings: ${}".format(total_sell - total_buy)
    print "shares traded: {}".format(shares_traded)

    if (buy_count - sell_count > 0):
        print "outstanding shares: {}".format(buy_count - sell_count)

        last_price = rb.quote_data(ticker)['last_trade_price']

        current_value = (buy_count - sell_count) * float(last_price);

        print "current value: ${}".format(current_value)

        print "adjusted winnings: ${}".format(total_sell - total_buy + current_value)
