from Robinhood import Robinhood
from cmd import Cmd

class RhInteractive(Cmd):
  def do_quote(self, args):
    """Get stock quote(s)"""
    if len(args) == 0:
      rh.print_quote_data();
    else:
      argv = args.split(',');
      if len(argv) == 1:
        rh.print_quote_data(argv[0]);
      else:
        rh.print_quotes_data(argv);

  def do_cancel(self, args):
    """Cancel a pending order"""
    if len(args) == 0:
      print("Syntax: cancel [orderId]")
    else:
      rh.cancel_order(args);

  def do_buy(self, args):
    """Submit buy order"""
    argv = args.split();

    if len(argv) < 3:
      print("Syntax: buy [symbol] [quanitity] [price]");
    else:
      stock_instrument = rh.instruments(argv[0]);

      if not len(stock_instrument):
        print("{} symbol not found".format(argv[0]));
      else:
        stock_instrument = stock_instrument[0];
        order = rh.place_buy_order(stock_instrument, float(argv[1]), float(argv[2]));

        if "detail" in order:
          print("Error: {}".format(order["detail"]));
        else:
          print("Buy order {} {} shares at ${}".format(order["quantity"], argv[0], round(float(order["price"]), 4)));
          print("  Type: {}".format(order["type"]));
          print("  Order id: {}".format(order["id"]));

          if order["reject_reason"] != None:
            print("Rejected: {}".format(order["reject_reason"]));
          print("  Order state: {}".format(order["state"]));
          print(" {} shares bought at average price of ${}".format(round(float(order["cumulative_quantity"])), 0 if order["average_price"] == None else round(float(order["average_price"]), 4)));

  def do_sell(self, args):
    """Submit sell order"""
    argv = args.split();

    if len(argv) < 3:
      print("Syntax: sell [symbol] [quanitity] [price]");
    else:
      stock_instrument = rh.instruments(argv[0])[0];
      order = rh.place_sell_order(stock_instrument, float(argv[1]), float(argv[2]));

      if "detail" in order:
        print("Error: {}".format(order["detail"]));
      else:
        print("Sell order {} {} shares at ${}".format(order["quantity"], argv[0], round(float(order["price"]), 4)));
        print("  Type: {}".format(order["type"]));
        print("  Order id: {}".format(order["id"]));

        if order["reject_reason"] != None:
          print("Rejected: {}".format(order["reject_reason"]));
        print("  Order state: {}".format(order["state"]));
        print(" {} shares bought at average price of ${}".format(round(float(order["cumulative_quantity"])), 0 if order["average_price"] == None else round(float(order["average_price"]), 4)));

  def do_value(self, args):
    """Show portfolio value"""

    data = rh.portfolios();

    previous_close = float(data["adjusted_equity_previous_close"]);
    equity = float(data["equity"]);
    if data["extended_hours_equity"] != None:
      equity = float(data["extended_hours_equity"]);

    change = equity - previous_close;
    percentChange = round(100 * change / previous_close, 3);

    print("Account Value: ${} | ${} ({}%)".format(equity, change, percentChange));

  def do_exit(self, args):
    """Quits the program"""
    raise SystemExit

  def precmd(self, line):
    if len(line) >= 1:
      argv = line.split();

      if len(argv[0]) == 1:
        if argv[0] == 'v':
          line = "value " + line[1:]
        elif argv[0] == 'q':
          line = "quote " + line[1:]
        elif argv[0] == 'c':
          line = "cancel " + line[1:]
        elif argv[0] == 'b':
          line = "buy " + line[1:]
        elif argv[0] == 's':
          line = "sell " + line[1:]
    return line

rh = Robinhood();

try:
  if rh.login_prompt() == False:
    print("Login error")
    raise SystemExit

  # rh.login(username="xxx", password="yyy")

  prompt = RhInteractive();
  prompt.prompt = '> ';
  prompt.cmdloop();
except KeyboardInterrupt:
  print('')
  raise SystemExit
