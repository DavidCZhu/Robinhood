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

page = get_first_page(rb);

orders = [order_item_info(order, rb, instruments_db) for order in page['results']]

sells = []
sell_count = {}
sell_date = {}

buys = []
buy_count = {}

yesterday = datetime.datetime.today().replace(tzinfo=None) - datetime.timedelta(hours=16);

for order in orders:
    order_date = dateutil.parser.parse(order['date']).replace(tzinfo=None)

    if yesterday < order_date:
        if float(order['shares']) > 0:
            if order['side'] == 'sell':
                sells.append(order)

                key = order['symbol']
                if key in sell_count:
                    sell_count[key] = sell_count[key] + float(order['shares'])
                else:
                    sell_count[key] = float(order['shares'])

                if key not in sell_date:
                    sell_date[key] = order_date;
                    

while (sell_count != buy_count):
    for order in orders:
        buy_date = dateutil.parser.parse(order['date']).replace(tzinfo=None)

        if order['side'] == 'buy' and float(order['shares']) > 0:
            key = order['symbol']

            if key in sell_count:

                if buy_date > sell_date[key]:
                    continue

                n_sold = sell_count[key]
                n_bought = 0;
                if key in buy_count:
                    n_bought = buy_count[key];

                if n_bought < n_sold:
                    if n_bought + float(order['shares']) <= n_sold:
                        buys.append(order);
                        if key in buy_count:
                            buy_count[key] = n_bought + float(order['shares'])
                        else:
                            buy_count[key] = float(order['shares']);
                    else:
                        order['shares'] = n_sold - n_bought
                        buys.append(order);
                        if key in buy_count:
                            buy_count[key] = n_bought + float(order['shares'])
                        else:
                            buy_count[key] = float(order['shares']);

    # get new orders
    page = get_next_history_page(rb, page['next'])
    orders = [order_item_info(order, rb, instruments_db) for order in page['results']]


total_buy = 0
total_sell = 0

print "BUY SELL MATCH"
print buy_count == sell_count
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

print "total winnings:"
print total_sell - total_buy


# print buy_count == sell_count

# orders = [order_item_info(order, rb, instruments_db) for order in past_orders]

# keys = ['side', 'symbol', 'shares', 'price', 'date', 'state']
# with open('orders.csv', 'w') as output_file:
#     dict_writer = csv.DictWriter(output_file, keys)
#     dict_writer.writeheader()
#     dict_writer.writerows(orders)

