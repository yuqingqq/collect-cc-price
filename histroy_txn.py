import requests
import pandas as pd
import json
import datetime
from bs4 import BeautifulSoup
from typing import List,Dict
import time
class btc_his():
    def __init__(self):
        self._addrlist = []
        self.get_top100_rich()

    def get_addr(self,s:str)->str:
        start = s.find('address')
        end = s.find('>',start,len(s))
        return s[start+8:end-1]

    def get_top100_rich(self):
        url="https://bitinfocharts.com/zh/top-100-richest-bitcoin-addresses.html"
        html_content = requests.get(url).text
        # Parse the html content
        soup = BeautifulSoup(html_content, "lxml")
        top100table = soup.find("table", attrs={"id": "tblOne"})
        top100rich = top100table.tbody.find_all('tr')
        for tr in top100rich:
            # print(tr)
            td = tr.find_all("td")[1]
            link = str(td.find_all('a'))
            self._addrlist.append(self.get_addr(link))
        print('endhere')
        top100table = soup.find("table",attrs={'id':'tblOne2'})
        top100rich = top100table.find_all('a')
        for link in top100rich:
            link = str(link)
            if link.find('https') == -1:continue
            self._addrlist.append(self.get_addr(link))
        print(f'size is {len(self._addrlist)}')

    def get_historical_balance_btc(self):
        geturl = 'https://blockchain.info/rawaddr/'
        his_data = []
        for addr in self._addrlist:
            r = requests.get(geturl + addr)
            if r == None: continue
            print(r)
            jsonr = r.json()
            print(jsonr)
            idx = len(jsonr['txs'])-1
            while idx>=0:
                txn = jsonr['txs'][idx]
                blockidx = txn['block_index']
                time = datetime.datetime.fromtimestamp(txn['time'])
                balance = txn['balance']*1e-8
                if idx == len(jsonr['txs'])-1:
                    change = balance
                else:
                    change = balance - his_data[-1][-1]
                his_data.append([addr,blockidx,time,balance,change])
                idx -= 1
            time.sleep(0.15)
        his_data_pd = pd.DataFrame(his_data,columns=['address','block','time','balance','change'])
        his_data_pd.to_csv('his_balance.csv')

if __name__ == '__main__':
    bh = btc_his()
    bh.get_historical_balance_btc()


# addr = '34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo'
# geturl = 'https://blockchain.info/rawaddr/'
# # geturl ='https://api.blockcypher.com/v1/btc/main/addrs/'+addr+'/full'
# r  = requests.get(geturl+addr)
# # print(r.url)
# # print(r.json())
# jsonr = r.json()
# print(type(jsonr))
# print(jsonr.keys())
# print(jsonr['address'])
# print(jsonr['n_tx'])
# print(jsonr['total_received'])
# print(jsonr['total_sent'])
# print(jsonr['final_balance'])
# print(type(jsonr['txs']))
#
# txn = jsonr['txs'][0]
# print(txn.keys())
# for i in range(len(jsonr['txs'])):
#     txn = jsonr['txs'][i]
#     print(txn['balance']*1e-8)
#     if i >5 : break
# print(datetime.datetime.fromtimestamp(txn['time']))
# print(txn['block_index'])

