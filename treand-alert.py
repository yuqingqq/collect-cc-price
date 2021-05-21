from typing import List,Dict
import snscrape.modules.twitter as sntwitter
import pandas as pd
from requests_oauthlib import OAuth1Session
import datetime
import re
import operator
import numpy as np
import sys
import csv

class TrendAlert:

    def __init__(self,  hashtag:str = '#Bitcoin OR #Ether OR #ether OR #bitcoin'):
        self._hashtag:str = hashtag
        self._PastN:int = 100
       # self.init_writer()

    def my_criteria(self,inf:List[float])->bool:
        crit = [10,10,0]
        if inf>=crit:
            return True
        return False

    def retrive_hashtags(self,content:str)->List[str]:
        return re.findall('#\w+', content)

    def alert_criteria(self, userinf:List[float], tweetinf:List[float]):
        mycriteria = [i for i in userinf]
        print(f'tweet inf {tweetinf}, crit {mycriteria}')
        if tweetinf>=mycriteria and tweetinf>=[100,50,0]:
            return True
        return False

    def make_alert(self,content:str):
        self.file = open('data.txt', 'a', encoding='utf-8')
        self.file.write(content)
        self.file.close()

    def retrieve_trends(self):
        today = datetime.date.today()
        query :str = self._hashtag + ' since:' + str(today)
        print(f'query is {query}')
        totaltweets = sntwitter.TwitterSearchScraper(query)
        for i, tweet in enumerate(totaltweets.get_items()):
            #print(tweet.date)
            #print(tweet.content)
            if tweet == None: continue
            inf :List[float]= [tweet.retweetCount, tweet.likeCount, tweet.replyCount]
            if inf == []: continue
            if self.my_criteria(inf):
                thisuser: str = tweet.user.username
                print(f'influencer {thisuser}')
                untilday = tweet.date.date()
                last_N_tweets = sntwitter.TwitterSearchScraper('from:' + thisuser +' until:'+str(untilday)).get_items()
                infthisuer:List[List[float]] = []
                for N, tweet_user in enumerate(last_N_tweets):
                    if tweet_user == None: continue
                    # print(tweet_user.date)
                    if N > self._PastN:
                        break
                    #got_hashtags = self.retrive_hashtags(content=tweet_user.content)
                    if N <= self._PastN:
                        infthisuer.append([tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount])
                if len(infthisuer) > 0:
                    infthisuer = np.array(infthisuer, dtype=np.float32)
                    avg = infthisuer.mean(0)
                    userinf = [avg[0], avg[1], avg[2]]
                    if self.alert_criteria(userinf,inf):
                        content = tweet.content.replace('\n', '').replace('\r', '')
                        userinf_str:str = str(userinf[0])+","+str(userinf[1])+","+str(userinf[2])
                        tweet_inf:str = str(inf[0])+","+str(inf[1])+","+str(inf[2])
                        alert_content = '\n'+tweet.url+' / '+str(tweet.date)+" / user inf "+ userinf_str+" / tweet inf "+tweet_inf+\
                                        " / "+tweet.user.username+" / "+content+'\n'
                        self.make_alert(alert_content)


if __name__ == "__main__":

    trendalert = TrendAlert()
    trendalert.retrieve_trends()