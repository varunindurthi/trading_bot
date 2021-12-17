import logging
import requests
import pprint
import time 
import hmac
import hashlib
from urllib.parse import urlencode
import threading
import websocket
import json

logger = logging.getLogger()

class BinanceFuturesClient:
    def __init__(self, public_key, secret_key, testnet):
        if testnet:
            self.base_url = 'https://testnet.binancefuture.com'
            self.wss_url = 'wss://stream.binancefuture.com/ws'
        else:
            self.base_url = 'https://fapi.binance.com'
            self.wss_url = 'wss://fstream.binancefuture.com/ws'
        
        self.public_key = public_key
        self.secret_key = secret_key

        self.headers = {'X-MBX-APIKEY':self.public_key}

        self.prices = dict()

        self.id = 1
        self.ws = None

        t = threading.Thread(target=self.start_ws)
        t.start()       

        logger.info('Binance Futures Client successfully initialized')

    def generate_signature(self, data):
        return hmac.new(self.secret_key.encode(), urlencode(data).encode(), hashlib.sha256).hexdigest()   

    def make_request(self, method, endpoint, data):
        if method == 'GET':
            response = requests.get(self.base_url + endpoint, params=data, headers=self.headers)

        elif method == 'POST':
            response = requests.post(self.base_url + endpoint, params=data, headers=self.headers)
        
        elif method == 'DELETE':
            response = requests.delete(self.base_url + endpoint, params=data, headers=self.headers)

        else:
            raise ValueError()
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error('Error while making {} request to {}: {} error code {}'.format(
                method,endpoint, response.json(), response.status_code))
            
            return None
    
    def get_contracts(self):
        exchange_info = self.make_request('GET', '/fapi/v1/exchangeInfo', None)

        contracts = {}

        if exchange_info is not None:
            for contract_data in exchange_info['symbols']:
                contracts[contract_data['pair']] = contract_data
        return contracts

    def get_historical_candles(self, symbol, interval):
        data = dict()
        data['symbol'] = symbol
        data['interval'] = interval
        data['limit'] = 1000

        raw_candles = self.make_request('GET', '/fapi/v1/klines', data)

        candles = []

        if raw_candles is not None:
            for c in raw_candles:
                candles.append([c[0], float(c[1]), float(c[2]), float(c[3]), float(c[4]), float(c[5])])
        
        return candles
    
    def get_bid_ask(self, symbol):
        data = dict()
        data['symbol'] = symbol
        ob_data  = self.make_request('GET', '/fapi/v1/ticker/bookTicker', data)

        if ob_data is not None:
            if symbol not in self.prices:
                self.prices[symbol] = {'bid': float(ob_data['bidPrice']), 'ask': float(ob_data['askPrice'])}
            else:
                self.prices[symbol]['bid'] = float(ob_data['bidPrice'])
                self.prices[symbol]['ask'] = float(ob_data['askPrice'])

        return self.prices[symbol]
    
    def get_balance(self):
        data = dict()
        data['timestamp'] = int(time.time()*1000)
        data['signature'] = self.generate_signature(data)

        balances = dict()

        account_data = self.make_request('GET', '/fapi/v1/account', data)

        if account_data is not None:
            for a in account_data['assets']:
                balances[a['asset']] = a
            
        return balances

    def place_order(self, symbol, side, quantity, order_type, price=None, tif=None):
        data = dict()
        data['symbol'] = symbol
        data['side'] = side
        data['quantity'] = quantity
        data['type'] = order_type
        
        if price is not None:
            data['price'] = price
        
        if tif is not None:
            data['timeInForce'] = tif
        
        data['timestamp'] = int(time.time()*1000)
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request('POST', '/fapi/v1/order', data)

        return order_status
    
    def cancel_order(self, symbol, order_id):
        data = dict()
        data['orderId'] = order_id
        data['symbol'] = symbol

        data['timestamp'] = int(time.time()*1000)
        data['signature'] = self.generate_signature(data)

        order_status = self.make_request('DELETE', '/fapi/v1/order', data)
        return order_status
    
    def get_order_status(self, symbol, order_id):

        data = dict()
        data['timestamp'] = int(time.time()*1000)
        data['signature'] = self.generate_signature(data)
        data['symbol'] = symbol
        data['order_id'] = order_id

        order_status = self.make_request('GET', '/fapi/v1/order', data)

        return order_status
    
    def start_ws(self):
        self.ws = websocket.WebSocketApp(self.wss_url, on_open=self.on_open, on_close=self.on_close, on_error=self.on_error, on_message=self.on_message)
        self.ws.run_forever()
        return
    
    def on_open(self):
        logger.info('Binance connection opened')
        self.subscribe_channel('BTCUSDT')
    
    def on_close(self):
        logger.warning('Binance websocket connection closed')
    
    def on_error(self, msg):
        logger.error('Binance websocket connection error: %s', msg)
    
    def on_message(self, msg):        
        data = json.loads(msg)

        if 'e' in data:
            if data['e'] == 'bookTicker':

                symbol = data['s']

                if symbol not in self.prices:
                    self.prices[symbol] = {'bid': float(data['b']), 'ask': float(data['a'])}
                else:
                    self.prices[symbol]['bid'] = float(data['b'])
                    self.prices[symbol]['ask'] = float(data['a'])
                
                print(self.prices[symbol])
                    


    def subscribe_channel(self, symbol):
        data = dict()
        data['method'] = 'SUBSCRIBE'
        data['id'] = self.id
        data['params'] = []
        data['params'].append(symbol.lower() + '@bookTicker')
       
        self.ws.send(json.dumps(data))

        self.id+=1






    
