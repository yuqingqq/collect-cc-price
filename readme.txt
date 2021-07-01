trend-alert: 
	Retrieve today's tweets (reweets>=10, likes>=10) and initialize the tweet user's historical influence (retweet,like,reply),
	Constantly retrieve the tweets satisfying (reweets>=10, likes>=10), if the tweet's influence is greater than user's historical influence, make the alert.
	Constantly retrieve the popular trends all over the world, if it contains the user defined key word, make the alert.

Output-> data.txt
Format: tweet url / tweet date / user's influence / tweet influence / user name / content

ctyptodata: 
Input: symbol. e.g., BTC-USD
	Constantly fetch estimation funding rate, order book, trades on huobi.

Output->data.csv
Trade format: id / timestamp / tradeId / amount (trade volume) / price / direction (buy or sell)
Order book: bids [[price,size]] / asks [[price,size]] / version (internal data) / timestamp
Estimation funding rate: localtime / type：efr / id / open price / close price / high price / amount (based on coin) / volume / count (0). 

histroy_txn.py:
	Get the top 100 eth holders and constantly retrieve information of the updates on their balance.

Output->bal_change.txt
	time / wallet address / wallet holder (if known) / change of balance
