import requests
import pandas as pd
import json
import datetime
from bs4 import BeautifulSoup
from typing import List,Dict
import time
from requests_html import HTMLSession
from selenium import webdriver
import  math

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
            time.sleep(2.0)
            if r == None: continue
            # print(r)
            jsonr = r.json()
            idx = len(jsonr['txs'])-1
            while idx>=0:
                txn = jsonr['txs'][idx]
                blockidx = txn['block_index']
                timehere = datetime.datetime.fromtimestamp(txn['time'])
                balance = txn['balance']*1e-8
                if idx == len(jsonr['txs'])-1:
                    change = balance
                else:
                    change = balance - his_data[-1][-1]
                his_data.append([addr,blockidx,timehere,balance,change])
                idx -= 1
        his_data_pd = pd.DataFrame(his_data,columns=['address','block','time','balance','change'])
        his_data_pd.to_csv('his_balance.csv')


class eth_update():
    def __init__(self):
        self._addrlist = pd.read_csv('addr.csv')
        # self._addrlist =[]
        self._eth_bal = {}
        self._name = {}

    def get_addr(self,s:str)->str:
        start = s.find('address')
        end = s.find('>',start,len(s))
        return s[start+8:end-1]

    def get_top_addr(self):
        urls = ["https://etherscan.io/accounts","https://etherscan.io/accounts/2","https://etherscan.io/accounts/3","https://etherscan.io/accounts/4"]
        for url in urls:
            driver = webdriver.Chrome()
            driver.maximize_window()
            driver.get(url)
            time.sleep(5)
            content = driver.page_source.encode('utf-8').strip()
            soup = BeautifulSoup(content, "html.parser")
            table = soup.find("table", {"class": "table table-hover"})
            trs = table.tbody.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                link = str(tds[1].find_all('a'))
                # print(link)
                name = str(tds[2])[4:-5]
                # print(name)
                addr = self.get_addr(link)
                self._name[addr] = name
                # print(addr)
                self._addrlist.append([addr,name])
            driver.quit()
        addrpd = pd.DataFrame(self._addrlist,columns=['addr','name'])
        addrpd.to_csv('addr.csv')

    def get_current_balance(self)->None:
        numaddr = len(self._addrlist)
        numit = numaddr//20
        bal_list = []
        for i in range(numit):
            url = 'https://api.etherscan.io/api?module=account&action=balancemulti&address='
            for j in range(19):
                addr = self._addrlist.iloc[i*20+j]['addr']
                url += addr+','
                self._name[addr] = self._addrlist.iloc[i*20+j]['name']
            url += self._addrlist.iloc[i*20+19]['addr']
            url += '&tag=latest&apikey=U6TVI4UT54WNRCBQMPN8F88TUF6YE2QMM2'
            result = requests.get(url).json()
            time.sleep(0.4)
            for item in result['result']:
                account = item['account']
                balance = float(item['balance'])
                self._eth_bal[account] = balance
                bal_list.append([account,balance])
                print(f'account {account} has balance {balance}')
        url = 'https://api.etherscan.io/api?module=account&action=balancemulti&address='
        if numit*20 != numaddr:
            for i in range(numaddr-numit*20-1):
                addr = self._addrlist.iloc[20*numit+i]['addr']
                url += addr+','
                self._name[addr] = self._addrlist.iloc[i * 20 + j]['name']
            url +=self._addrlist.iloc[-1]['addr']
            url += '&tag=latest&apikey=U6TVI4UT54WNRCBQMPN8F88TUF6YE2QMM2'
            result = requests.get(url).json()
            time.sleep(0.4)
            for item in result['result']:
                account = item['account']
                balance = float(item['balance'])
                bal_list.append([account, balance])
                self._eth_bal[account] = balance
                print(f'account {account} has balance {balance}')
        # print(self._eth_bal)
        # print(len(self._eth_bal.keys()))
        # bal_listpd = pd.DataFrame(bal_list)
        # bal_listpd.to_csv('bal.csv')
        # for account in result['result']:

    def write_change(self,addr:str,change:float,name:str)->None:
        file = open('bal_change.txt', 'a', encoding='utf-8')
        change = change*pow(10,-18)
        file.write(str(datetime.datetime.now()) + ' / '+addr+' / '+str(name)+'/  '+ str(change)+'\n')
        file.close()

    def observe_balance_change(self):
        numaddr = len(self._addrlist)
        numit = numaddr // 20
        for i in range(numit):
            url = 'https://api.etherscan.io/api?module=account&action=balancemulti&address='
            for j in range(19):
                addr = self._addrlist.iloc[i * 20 + j]['addr']
                url += addr + ','
            url += self._addrlist.iloc[i * 20 + 19]['addr']
            url += '&tag=latest&apikey=U6TVI4UT54WNRCBQMPN8F88TUF6YE2QMM2'
            result = requests.get(url).json()
            # print(result)
            time.sleep(0.4)
            for item in result['result']:
                account = item['account']
                balance = float(item['balance'])
                if balance == self._eth_bal[account]:
                    continue
                print(f'addr {account} updates')
                change = balance - self._eth_bal[account]
                self.write_change(account,change,self._name[account])
                self._eth_bal[account] = balance
        if numit*20 != numaddr:
            url = 'https://api.etherscan.io/api?module=account&action=balancemulti&address='
            for i in range(numaddr-numit*20-1):
                addr = self._addrlist.iloc[20*numit+i]['addr']
                url += addr+','
            url += self._addrlist.iloc[-1]['addr']
            url += '&tag=latest&apikey=U6TVI4UT54WNRCBQMPN8F88TUF6YE2QMM2'
            result = requests.get(url).json()
            time.sleep(0.4)
            for item in result['result']:
                account = item['account']
                balance = float(item['balance'])
                if balance == self._eth_bal[account]:
                    continue
                print(f'addr {account} updates')
                change = balance - self._eth_bal[account]
                self.write_change(account, change,self._name[addr])
                self._eth_bal[account] = balance

if __name__ == '__main__':
    eth = eth_update()
    eth.get_current_balance()
    while(1):
        eth.observe_balance_change()


    # eth.get_top_addr()

    # bh = btc_his()
    # bh.get_historical_balance_btc()

    # print(jsonr['txs'][0].keys())
    # print(jsonr['txs'][0]['size'])
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

