from flask import Flask, render_template, request
application = Flask(__name__)
app = application
import my_kucoin
import config
import pymysql
import datetime
import json
import logging
import hashlib
import base64
import requests
import time
import hmac

live = 0
mysql_host = "us-cdbr-east-06.cleardb.net"
mysql_dbname = "heroku_42b1a7a586099e3"
mysql_username = "b9bf09310bc7a9"
mysql_password = "a03f30ecf1dee90"
# mysql_host = "localhost"
# mysql_dbname = "trading"
# mysql_username = "root"
# mysql_password = ""
today = datetime.datetime.now()

# write and load log data for bot log table
conn = pymysql.connect(host=mysql_host,
                       user=mysql_username,
                       password=mysql_password,
                       db=mysql_dbname,
                       charset='utf8')
cur = conn.cursor()

@app.route('/', methods=['GET', 'POST'])
# @app.route('/<int:uid>', methods=['GET','POST'])
def index():
    bot_name = "botname"
    tradingpairs = "tradingpairs"
    passphrase = "password"
    timenow = "timenow"
    exchange = "exchange"
    ticker = "ticker"
    timeframe = "timeframe"
    position_size = "position size"
    order_action = "order action"
    order_contracts = "order contracts"
    order_price = "order price"
    order_id = "order id"
    market_position = "market postion"
    market_position_size = "market position size"
    transaction_order_id = "transaction order id"

    myKucoin = my_kucoin.Mykucoin(live)
    if passphrase == config.WEBHOOK_PASSPHRASE:
        sql = """insert into `bot_log` (id, bot_name, tradingpairs, bot_time, exchange, ticker, timeframe,
                 position_size, order_action, order_contracts, order_price, order_id, market_position,
                market_position_size, transaction_order_id, created_at, updated_at) values (NULL, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """

        # running query command
        conn.ping()  # reconnecting mysql
        conn.cursor().execute(sql, (
            bot_name, tradingpairs, timenow, exchange, ticker, timeframe, position_size,
            order_action, order_contracts, order_price, order_id, market_position, market_position_size,
            transaction_order_id, today, today))
        conn.commit()

    return render_template('home.html', json_result=myKucoin.get_ticker()[0], len=len(myKucoin.get_ticker()))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    api_key = config.API_KEY
    api_secret = config.API_SECURET
    api_passphrase = config.API_PASSWORD
    base_uri = config.DEMO_URL

    def get_headers(method, endpoint):
        now = int(time.time() * 1000)
        str_to_sign = str(now) + method + endpoint
        signature = base64.b64encode(
            hmac.new(api_secret.encode(), str_to_sign.encode(), hashlib.sha256).digest()).decode()
        passphrase = base64.b64encode(
            hmac.new(api_secret.encode(), api_passphrase.encode(), hashlib.sha256).digest()).decode()
        return {'KC-API-KEY': api_key,
                'KC-API-KEY-VERSION': '2',
                'KC-API-PASSPHRASE': passphrase,
                'KC-API-SIGN': signature,
                'KC-API-TIMESTAMP': str(now)
                }

    # Getting Query Transaction Records
    method = 'GET'
    endpoint = '/api/v2/account-overview?currency=USDT'
    accountOverview = requests.request(method, base_uri + endpoint, headers=get_headers(method, endpoint))

    # Getting Accounts Balance(historical-trades)
    method = 'GET'
    endpoint = '/api/v2/orders/historical-trades?symbol=BTCUSDTM'
    transactionHistoricalTrades = requests.request(method, base_uri + endpoint, headers=get_headers(method, endpoint))

    # empty list
    historical_trades_id_list = []
    order_id_list = []
    symbol_list = []
    time_list = []
    side_list = []
    size_list = []
    price_list = []
    fee_list = []
    fee_rate_list = []
    history_place_type_list = []
    order_type_list = []
    fee_currency_list = []
    pnl_list = []
    pnl_currency_list = []
    value_list = []
    maker_list = []
    force_taker_list = []

    for data in transactionHistoricalTrades.json()['data']:
        historical_trades_id_list.append(data['id'])
        order_id_list.append(data['orderId'])
        symbol_list.append(data['symbol'])
        time_list.append(data['time'])
        side_list.append(data['side'])
        size_list.append(data['size'])
        price_list.append(data['price'])
        fee_list.append(data['fee'])
        fee_rate_list.append(data['feeRate'])
        history_place_type_list.append(data['placeType'])
        order_type_list.append(data['orderType'])
        fee_currency_list.append(data['feeCurrency'])
        pnl_list.append(data['pnl'])
        pnl_currency_list.append(data['pnlCurrency'])
        value_list.append(data['value'])
        maker_list.append(data['maker'])
        force_taker_list.append(data['forceTaker'])

    # running query command
    conn.ping()  # reconnecting mysql
    i = 0
    with conn:
        with conn.cursor() as cur:
            for historical_trades_id in historical_trades_id_list:
                cur.execute("SELECT * FROM historical_trades WHERE historical_trades_id=%s", (historical_trades_id))
                if cur.rowcount == 0:
                    sql = """insert into `historical_trades` (id, historical_trades_id, order_id, symbol, time, side, size, price, 
                                                fee, fee_rate, place_type, order_type, fee_currency, pnl, pnl_currency, value, maker, 
                                                force_taker, created_at, updated_at) values (NULL, %s, 
                                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
                    conn.cursor().execute(sql, (
                        historical_trades_id, order_id_list[i], symbol_list[i], time_list[i], side_list[i], size_list[i],
                        price_list[i], fee_list[i], fee_rate_list[i], history_place_type_list[i], order_type_list[i],
                        fee_currency_list[i], pnl_list[i], pnl_currency_list[i], value_list[i], str(maker_list[i]), str(force_taker_list[i]),
                        today, today))
                    conn.commit()
                i = i + 1

    # Getting Accounts Balance(history)
    method = 'GET'
    endpoint = '/api/v2/orders/history?symbol=BTCUSDTM'
    transactionHistory = requests.request(method, base_uri + endpoint, headers=get_headers(method, endpoint))

    # empty list
    history_id_list = []
    history_symbol_list = []
    history_type_list = []
    history_side_list = []
    history_price_list = []
    history_size_list = []
    history_deal_size_list = []
    history_deal_value_list = []
    history_working_type_list = []
    history_stop_price_list = []
    history_timeIn_force_list = []
    history_post_only_list = []
    history_hidden_list = []
    history_leverage_list = []
    history_close_order_list = []
    history_visible_size_list = []
    history_remark_list = []
    history_order_time_list = []
    history_reduce_only_list = []
    history_status_list = []
    history_place_type_list = []
    history_take_profit_price_list = []
    history_cancel_size_list = []
    history_client_oid_list = []

    for data in transactionHistory.json()['data']:
        history_id_list.append(data['id'])
        history_symbol_list.append(data['symbol'])
        history_type_list.append(data['type'])
        history_side_list.append(data['side'])
        history_price_list.append(data['price'])
        history_size_list.append(data['size'])
        history_deal_size_list.append(data['dealSize'])
        history_deal_value_list.append(data['dealValue'])
        history_working_type_list.append(data['workingType'])
        history_stop_price_list.append(data['stopPrice'])
        history_timeIn_force_list.append(data['timeInForce'])
        history_post_only_list.append(data['postOnly'])
        history_hidden_list.append(data['hidden'])
        history_leverage_list.append(data['leverage'])
        history_close_order_list.append(data['closeOrder'])
        history_visible_size_list.append(data['visibleSize'])
        history_remark_list.append(data['remark'])
        history_order_time_list.append(data['orderTime'])
        history_reduce_only_list.append(data['reduceOnly'])
        history_status_list.append(data['status'])
        history_place_type_list.append(data['placeType'])
        history_take_profit_price_list.append(data['takeProfitPrice'])
        history_cancel_size_list.append(data['cancelSize'])
        history_client_oid_list.append(data['clientOid'])

    # running query command
    conn.ping()  # reconnecting mysql
    i = 0
    with conn:
        with conn.cursor() as cur:
            for history_id in history_id_list:
                cur.execute("SELECT * FROM history WHERE history_id=%s", (history_id))
                if cur.rowcount == 0:
                    sql = """insert into `history` (id, history_id, symbol, type, side, price, size, deal_size,
                                                deal_value, working_type, stop_price, timeIn_force, post_only, hidden, leverage, close_order, visible_size,
                                                remark, order_time, reduce_only, status, place_type, take_profit_price, cancel_size, client_oid, created_at,
                                                updated_at) values (NULL, %s, %s, %s, %s, %s, %s, %s,
                                                %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
                    conn.cursor().execute(sql, (
                        history_id, history_symbol_list[i], history_type_list[i], history_side_list[i], history_price_list[i],
                        history_size_list[i],
                        history_deal_size_list[i], history_deal_value_list[i], history_working_type_list[i], str(history_stop_price_list[i]), history_timeIn_force_list[i],
                        str(history_post_only_list[i]), str(history_hidden_list[i]), history_leverage_list[i], str(history_close_order_list[i]), str(history_visible_size_list[i]),
                        str(history_remark_list[i]), history_order_time_list[i], str(history_reduce_only_list[i]), history_status_list[i], history_place_type_list[i], str(history_take_profit_price_list[i]),
                        history_cancel_size_list[i], history_client_oid_list[i], today, today))
                    conn.commit()
                i = i + 1

    # calculate count of unique bots
    conn.ping()  # reconnecting mysql
    i = 0
    with conn:
        with conn.cursor() as cur:
            for history_id in history_id_list:
                cur.execute("SELECT * FROM bot_log WHERE exchange = 'KUCOIN' AND bot_time >= DATE_SUB(NOW(),INTERVAL 1 HOUR)")
                past_one_hour = cur.rowcount
                cur.execute(
                    "SELECT * FROM bot_log WHERE exchange = 'KUCOIN' AND bot_time >= DATE_SUB(NOW(),INTERVAL 24 HOUR)")
                past_one_day = cur.rowcount
                cur.execute(
                    "SELECT * FROM bot_log WHERE exchange = 'KUCOIN' AND bot_time >= DATE_SUB(NOW(),INTERVAL 1 WEEK)")
                past_one_week = cur.rowcount
                cur.execute(
                    "SELECT * FROM bot_log WHERE exchange = 'KUCOIN' AND bot_time >= DATE_SUB(NOW(),INTERVAL 1 MONTH)")
                past_one_month = cur.rowcount


    return render_template('dashboard.html', walletBalance=accountOverview.json()['data'][0]['walletBalance'], transactionHistory=transactionHistory.json()
           ,pastOneHour = past_one_hour, pastOneDay = past_one_day, pastOneWeek = past_one_week, pastOneMonth = past_one_month)


if __name__ == "__main__":
    # application.debug = True
    application.run(threaded=True)
