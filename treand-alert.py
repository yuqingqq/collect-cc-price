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
import asyncio
import twitter
import json

class TrendAlert:

    def __init__(self,  hashtag:str = '#Bitcoin OR #Ether OR #ether OR #bitcoin'):
        self._hashtag:str = hashtag
        self._PastN:int = 100
        self._userinf:Dict = {}
       # self.init_writer()

    def my_criteria(self,inf:List[float])->bool:
        crit = [10,10,0]
        if inf>=crit:
            return True
        return False

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

    async def retrieve_popular_trends(self,keywords:List[str] = ['crypto','btc','eth','cryptocurrency','doge','swap']):
        while(1):
            CONSUMER_KEY = 'pHx92656vKOFAvtCHsI3fNJWR'
            CONSUMER_SECRET = 'IHnOKx3ijunaE0d9ULskaHSCdaCI3Qg8QtWhmGVjllYSu1d1Jf'
            OAUTH_TOKEN = '1379301855734296576-E1gmhjomb7MhNoEVhQq8xDWv6sNOBt'
            OAUTH_TOKEN_SECRET = '7rx4a3rctCa71baFYesIlwESZ0ifzNo0rPTn8uXQMiXvK'
            auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                                       CONSUMER_KEY, CONSUMER_SECRET)

            twitter_api = twitter.Twitter(auth=auth)
            # print(twitter_api)
            world_trends = twitter_api.trends.place(_id=1)
            for trend in world_trends[0]['trends']:
                print(trend)
                for key in keywords:
                    if key in trend['name']:
                        print('find topic')
                        content = '\n'+ trend['name']+ " / "+ trend['url']+" / "+ trend['tweet_volume']+'\n'
                        self.make_alert(content)
            await asyncio.sleep(60)

    async def retrieve_trends(self):
        while(1):
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
                    userinf = []
                    if thisuser in self._userinf.keys():
                        userinf = self._userinf[thisuser]
                    else:
                        for N, tweet_user in enumerate(last_N_tweets):
                            if tweet_user == None: continue
                            # print(tweet_user.date)
                            if N > self._PastN:
                                break
                            #got_hashtags = self.retrive_hashtags(content=tweet_user.content)
                            if N <= self._PastN:
                                infthisuer.append([tweet_user.retweetCount, tweet_user.likeCount, tweet_user.replyCount])
                        if len(infthisuer) ==0: continue
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
            await asyncio.sleep(1800)

async def main():
    trendalert = TrendAlert()
    await asyncio.gather(
        trendalert.retrieve_popular_trends(),
        trendalert.retrieve_trends()
    )

asyncio.run(main())

    # trendalert.retrieve_trends()