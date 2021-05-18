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
import csv
import asyncio


class ccdata:
    def __init__(self,symbol:str = 'btcusdt',type:str= 'swap'):
        self._symbol = symbol
        self._type = type
        self.init_writer()

    def init_writer(self):
        file = open('data.csv','a')
        self._writer = csv.writer(file)

    async def fetch_swap_trade(self):
        tradeStr_Trades = '''{
                    "sub": "market.''' + self._symbol + '''.trade.detail",
                    "id":"id7"
                }'''
        ws = self.make_connection(require='trade')
        ws.send(tradeStr_Trades)
        while(1):
            compressData: str = ws.recv()
            result: str = gzip.decompress(compressData).decode('utf-8')
            print(result)
            if result[:5] == '{"id"':
                continue
            if result[:7] == '{"ping"':
                ts = result[8:21]
                pong = '{"pong":' + ts + '}'
                ws.send(pong)
                continue
            result_js: Dict[str, str] = json.loads(result)
            row = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    'trade',
                    pd.to_datetime(result_js['ts'],unit='ms')+ pd.Timedelta('08:00:00'),
                    result_js['tick']['id'],
                    pd.to_datetime(result_js['tick']['ts'],unit='ms')+ pd.Timedelta('08:00:00')]
            for trade in result_js['tick']['data']:
                row += [trade['amount'],
                        pd.to_datetime(trade['ts'],unit='ms')+ pd.Timedelta('08:00:00'),
                        trade['id'],trade['price'],trade['direction'],trade['quantity']]
            self._writer.writerow(row)
            await asyncio.sleep(1.0/20)
                # localtime: 11/5/2021 7:22:11
                # type: trade
                # ts1:1603708208346, Request time
                # id: 131602265, Unique Order Id(symbol level).
                # ts2: 1603708208335, tick time
                # amount: 2, quantity(Cont.). Sum of both buy and sell sides
                # ts: 1603708208335, trade timestamp
                # id: 1316022650000, Unique Transaction Id(symbol level)
                # price: 13073.3,
                # direction: "buy",
                # quantity: 0.002, trading quantity(coin)

    async def fetch_swap_efr(self):
        print('fetching efr')

        while (1):
            traderStr_estimated_funding_rate = '''{
                "sub": "market.''' + self._symbol + '''.estimated_rate.1min",
                "id": "id4"
            }'''
            ws = self.make_connection(require='efr')
            ws.send(traderStr_estimated_funding_rate)
            compressData: str = ws.recv()
            result: str = gzip.decompress(compressData).decode('utf-8')
            print(result)
            if result[:5] == '{"id"':
                continue
            if result[:7] == '{"ping"':
                ts = result[8:21]
                pong = '{"pong":' + ts + '}'
                ws.send(pong)
                continue
            result_js: Dict[str, str] = json.loads(result)
            row :List[str]= [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'efr',
                   pd.to_datetime(result_js['ts'], unit='ms') + pd.Timedelta('08:00:00'),
                   result_js['tick']['id'], result_js['tick']['open'], result_js['tick']['close'],
                   result_js['tick']['high'], result_js['tick']['low'],
                   result_js['tick']['amount'], result_js['tick']['vol'], result_js['tick']['count']]
            print(row)
            self._writer.writerow(row)
            await asyncio.sleep(30)
            # localtime: 11/5/2021 7:22:11
            # type: efr
            # id: 1603708560, index kline id,the same as kline timestamp
            # open: 0.0001,	open index price
            # close: 0.0001, close index price
            # high: 0.0001, highest index price
            # low: 0.0001, lowest index price
            # amount: 0, amount based on coins.
            # vol: 0, 	Trade Volume(Cont.). The value is 0.
            # count: 0, The value is 0.

    async def fetch_swap_depth(self):
        print('fetching depth')
        tradeStr_marketDepth = '''{
            "sub": "market.''' + self._symbol + '''.depth.step2",
            "id": "id3"
        }'''
        ws = self.make_connection(require='depth')
        ws.send(tradeStr_marketDepth)
        while(1):
            compressData: str = ws.recv()
            result: str = gzip.decompress(compressData).decode('utf-8')
            print(result)
            if result[:5] == '{"id"':
                continue
            if result[:7] == '{"ping"':
                ts = result[8:21]
                pong = '{"pong":' + ts + '}'
                ws.send(pong)
                continue
            result_js: Dict[str, str] = json.loads(result)
            row:List[str] = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'dob',
                   pd.to_datetime(result_js['ts'], unit='ms') + pd.Timedelta('08:00:00'),
                   result_js['tick']['mrid'],
                   pd.to_datetime(result_js['tick']['ts'], unit='ms') + pd.Timedelta('08:00:00'),
                   result_js['tick']['id']]
            row += [bid for bid in result_js['tick']['bids']]
            row += [ask for ask in result_js['tick']['asks']]
            row += [result_js['tick']['version']]
            self._writer.writerow(row)
            await asyncio.sleep(1.0/20)
            # localtime: 11/5/2021 7:22:11
            # type : dob
            # ts :1603707576468, Time of Respond Generation, Unit: Millisecond
            # mrid: 131596447, Order ID
            # id: 1603707576,tick ID
            # bids: [[13071.9,38],[13068,5]],	Buy,[price(Bid price), vol(Bid orders(Cont.))], Price in descending sequence
            # asks: [[13081.9,197],[13099.7,371]], Sell,[price(Ask price), vol(Ask orders (cont.) )], price in ascending sequence
            # ts: 1603707576467,	Timestamp for depth generation; generated once every 100ms, unit: millisecond
            # version: 1603707576,version ID


    # async def fetch_swapdata(self):
    #
    #     task1 = asyncio.create_task(self.fetch_swap_trade())
    #     task2 = asyncio.create_task(self.fetch_swap_depth())
    #     task3 = asyncio.create_task(self.fetch_swap_efr())
    #
    #     # tasks = [
    #     #         asyncio.ensure_future(job1),
    #     #         asyncio.ensure_future(job2),
    #     #         asyncio.ensure_future(job3)
    #     #         ]
    #     #
    #     # loop = asyncio.get_event_loop()
    #     # loop.run_until_complete(asyncio.wait(tasks))
    #     await task1
    #     await task2
    #     await task3

    def make_connection(self, require:str ='marketdata'):
        while (1):
            try:
                if self._type == 'swap':
                    if require == 'trade' or require =='depth':
                        ws = create_connection("wss://api.hbdm.com/swap-ws")
                        print('connect to trade')
                    # elif require == 'depth':
                    #     ws = create_connection("wss://api.btcgateway.pro/swap-ws")
                    #     print("connect to depth")
                    else:
                        print('connect to efr')
                        ws = create_connection("wss://api.hbdm.com/ws_index")
                if self._type == 'spot':
                    ws = create_connection("wss://api.huobi.pro/ws")
                break
            except:
                print('connect ws error,retry...')
                time.sleep(2)
        return ws

    def fetch_market_depth(self):
        header = ['local-time']
        for i in range(20):
            header += ['bid-price-'+str(i), 'bid-size-'+str(i),'ask-price-'+str(i),'ask-size'+str(i)]
        header += ['tick-time']
        tradeStr_marketDepth = """
        {
            "sub": "market."""+self._symbol+""".depth.step2", "id": "id1"
        }"""
        ws = self.make_connection()
        ws.send(tradeStr_marketDepth)
        trade_id = ''
        count = True
        while(1):
            compressData:str = self._ws.recv()
            result:str = gzip.decompress(compressData).decode('utf-8')
            if result[:5] == '{"id"': continue
            if result[:7] == '{"ping"':
                ts = result[8:21]
                pong = '{"pong":' + ts + '}'
                ws.send(pong)
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
        ws = self.make_connection()
        ws.send(tradeStr_tradeDetail)
        while(1):
            compressData:str = self._ws.recv()
            result = gzip.decompress(compressData).decode('utf-8')
            # print(result[:5])
            if result[:5] == '{"id"': continue
            if result[:7] == '{"ping"':
                ts = result[8:21]
                pong = '{"pong":' + ts + '}'
                ws.send(pong)
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

async def main():
    ccdata_btcusdt = ccdata(symbol='BTC-USD',type='swap')
    # task1 = asyncio.create_task( ccdata_btcusdt.fetch_swap_depth())
    # task2 = asyncio.create_task(ccdata_btcusdt.fetch_swap_trade())
    # task3 = asyncio.create_task(ccdata_btcusdt.fetch_swap_efr())
    await asyncio.gather(
        ccdata_btcusdt.fetch_swap_efr(),
        ccdata_btcusdt.fetch_swap_depth(),
        ccdata_btcusdt.fetch_swap_trade()
    )

asyncio.run(main())

    #ccdata_btcusdt.fetch_market_depth()
    # ccdata_btcusdt.fetch_trades()