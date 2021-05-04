import ccxt
from typing import Dict, List

class ccdata:
    def __init__(self,symbol:str = 'ETH/USDT'):
        self._symbol = symbol
        self._huobi = ccxt.huobipro({'enableRateLimit': True})
        self._market = self._huobi.load_markets()

    def fetch_orderbook(self)->Dict[str,str]:
        return self._huobi.fetch_l2_order_book(self._symbol,limit=self._huobi.rateLimit)

    def fetch_trades(self,limit:int = 150)->List[Dict[str,str]]:
        return self._huobi.fetch_trades(self._symbol,limit=limit)

if __name__ == "__main__":
    eth_to_usd = ccdata()
    bids: List[List[float]] = []
    asks: List[List[float]] = []
    info = ['price','amount','datetime','side']
    ongoing_trades: List[List[str]] = []
    rounds = 0
    while(rounds<10):
        orderbook = eth_to_usd.fetch_orderbook()
        bids = orderbook['bids']
        asks = orderbook['asks']
        buys :List[List[str]] = []
        sells :List[List[str]] = []
        trades = eth_to_usd.fetch_trades()
        for t in trades:
            if t['side'] == 'buy':
                buys.append([t['price'],t['amount'],t['datetime']])
            else:
                sells.append([t['price'],t['amount'],t['datetime']])
        print('time is :',orderbook['datetime'])
        print('bids:',bids)
        print('asks:',asks)
        print('buys:',buys)
        print('sells:',sells)
        rounds+=1
