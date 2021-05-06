# import ccxt
# from typing import Dict, List
#
# class ccdata:
#     def __init__(self,symbol:str = 'ETH/USDT'):
#         self._symbol = symbol
#         self._huobi = ccxt.huobipro({'enableRateLimit': True})
#         self._market = self._huobi.load_markets()
#
#     def fetch_orderbook(self)->Dict[str,str]:
#         return self._huobi.fetch_l2_order_book(self._symbol,limit=self._huobi.rateLimit)
#
#     def fetch_trades(self,limit:int = 150)->List[Dict[str,str]]:
#         return self._huobi.fetch_trades(self._symbol,limit=limit)
#
# if __name__ == "__main__":
#     eth_to_usd = ccdata()
#     bids: List[List[float]] = []
#     asks: List[List[float]] = []
#     info = ['price','amount','datetime','side']
#     ongoing_trades: List[List[str]] = []
#     rounds = 0
#     while(rounds<10):
#         orderbook = eth_to_usd.fetch_orderbook()
#         bids = orderbook['bids']
#         asks = orderbook['asks']
#         buys :List[List[str]] = []
#         sells :List[List[str]] = []
#         trades = eth_to_usd.fetch_trades()
#         for t in trades:
#             if t['side'] == 'buy':
#                 buys.append([t['price'],t['amount'],t['datetime']])
#             else:
#                 sells.append([t['price'],t['amount'],t['datetime']])
#         print('time is :',orderbook['datetime'])
#         print('bids:',bids)
#         print('asks:',asks)
#         print('buys:',buys)
#         print('sells:',sells)
#         rounds+=1
from websocket import create_connection
import gzip
import time
import json
from datetime import datetime
from typing import Dict, List
import  pandas as pd
class ccdata:
    def __init__(self,symbol = 'btcusdt'):
        self._symbol = symbol
        self.make_connection()

    def make_connection(self):
        while (1):
            try:
                self._ws = create_connection("wss://api.huobi.pro/ws")
                break
            except:
                print('connect ws error,retry...')
                time.sleep(5)

    def fetch_klline(self):
        tradeStr_kline :str= """{"sub": "market.""" + self._symbol+"""".1min",  "id": "id1"}"""
        self._ws.send(tradeStr_kline)
        compressData :str= self._ws.recv()
        result :str= gzip.decompress(compressData).decode('utf-8')
        result_js:Dict[str,str] = json.loads(result)
        print(result_js)

    def fetch_market_depth(self):
        header = ['local-time']
        for i in range(20):
            header += ['bid-price-'+str(i), 'bid-size-'+str(i),'ask-price-'+str(i),'ask-size'+str(i)]
        header += ['tick-time']
        tradeStr_marketDepth = """
        {
            "sub": "market."""+self._symbol+""".depth.step2", "id": "id1"
        }"""
        self._ws.send(tradeStr_marketDepth)
        trade_id = ''
        count = True
        while(1):
            compressData:str = self._ws.recv()
            result:str = gzip.decompress(compressData).decode('utf-8')
            if result[:5] == '{"id"': continue
            if result[:7] == '{"ping"':
                ts = result[8:21]
                pong = '{"pong":' + ts + '}'
                self._ws.send(pong)
                # self._ws.send(tradeStr_kline)
            else:
                try:
                    if trade_id == result['data']['id']:
                        print('same id')
                    else:
                        trade_id = result['data']['id']
                except Exception:
                    pass
                #     {
                #         "bids":[[54561.0, 1.174826], [54560.0, 0.054939]],  # The current all bids in format [price, size]
                #         "asks":[[54562.0, 0.32892], [54563.0, 0.002763]]  # The current all asks in format [price, size]
                #         "version":"126811697965",  # Internal data
                #         "ts":"1620200256929",  # The UNIX timestamp in milliseconds adjusted to Singapore time
                #     }
                result_js:Dict[str,str] = json.loads(result)
                print(result_js)
                result_pd = pd.DataFrame({'ts':[pd.to_datetime(result_js['ts'], unit='ms')+ pd.Timedelta('08:00:00')]})
                for i in range(20):
                    result_pd['bid-price-'+str(i)] = result_js['tick']['bids'][i][0]
                    result_pd['bid-size-'+str(i)] = result_js['tick']['bids'][i][1]
                    result_pd['ask-price-'+str(i)] = result_js['tick']['asks'][i][0]
                    result_pd['ask-size-'+str(i)] = result_js['tick']['asks'][i][1]
                result_pd['tick_time'] = pd.to_datetime(result_js['tick']['ts'] , unit='ms')+ pd.Timedelta('08:00:00')
                print(result_pd)
                if count:
                    result_pd.to_csv('orderbook.csv', index=False, mode='a', header=header)
                    count = False
                else:
                    result_pd.to_csv('orderbook.csv', index=False, mode='a', header=False)

    def fetch_trades(self):
        header = ['old-id','trade-time','new-id','amount','price','direction','local-time','tick-time']
        count = True
        tradeStr_tradeDetail = """
        {"sub": "market."""+self._symbol+""".trade.detail", "id": "id2"}"""
        self._ws.send(tradeStr_tradeDetail)
        while(1):
            compressData:str = self._ws.recv()
            result = gzip.decompress(compressData).decode('utf-8')
            # print(result[:5])
            if result[:5] == '{"id"': continue
            if result[:7] == '{"ping"':
                ts = result[8:21]
                pong = '{"pong":' + ts + '}'
                self._ws.send(pong)
                # self._ws.send(tradeStr_kline)
            else:
                try:
                    if trade_id == result['data']['id']:
                        print('same id')
                    else:
                        trade_id = result['data']['id']
                except Exception:
                    pass
                result_js: List[Dict[str, str]] = json.loads(result)
                #     {
                #         "id":126811369725267309467494213,  # Unique trade id (to be obsoleted)
                #         "ts":"1620200048835",  # Last trade time (UNIX epoch time in millisecond)
                #         "tradeId":"102410937503",  # Unique trade id (NEW)
                #         "amount":"0.002229",  # Last trade volume (buy side or sell side)
                #         "price":"54542.18",  # Last trade price
                #         "direction":"buy",  # Aggressive order side (taker's order side) of the trade: 'buy' or 'sell'
                #     }
                print(result_js)
                result_pd = pd.DataFrame(result_js['tick']['data'])
                result_pd['ts'] = pd.to_datetime(result_pd['ts'], unit='ms')+ pd.Timedelta('08:00:00')
                result_pd['local time'] = pd.to_datetime(result_js['ts'], unit='ms')+ pd.Timedelta('08:00:00')
                result_pd['tick time'] = pd.to_datetime(result_js['tick']['ts'], unit='ms')+ pd.Timedelta('08:00:00')
                print(result_pd)
                # result_pd = pd.DataFrame(result_ls)
                if count:
                    result_pd.to_csv('trade.csv', index=False,mode='a',header=header)
                    count = False
                else:
                    result_pd.to_csv('trade.csv',index=False,mode='a',header=False)

if __name__ == '__main__':
    ccdata_btcusdt = ccdata('ethusdt')
    ccdata_btcusdt.fetch_market_depth()
    # ccdata_btcusdt.fetch_trades()