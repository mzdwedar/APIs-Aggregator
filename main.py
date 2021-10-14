from typing import Optional

from requests.api import options
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn

from const import news_api, reddit_api
import requests
import requests.auth

import itertools
import json

app = FastAPI()

cache = dict()



def redditAPI(q:str = None):
    auth = requests.auth.HTTPBasicAuth(reddit_api['public key'], reddit_api['secret'])

    data = {'grant_type': 'password',
            'username': reddit_api['username'],
            'password': reddit_api['password']}

    headers = {'User-Agent': 'NEWSAPI'}

    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)

    TOKEN = res.json()['access_token']

    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

    if (q != None):
        res = requests.get(f"https://oauth.reddit.com/r/news/search/?q={q}&source=recent&restrict_sr=1",
                    headers=headers, params={'limit':'100'})
    else:
        res = requests.get("https://oauth.reddit.com/r/news",
                    headers=headers, params={'limit':'100'})

    if (res.status_code == 200):

        res = res.json()['data']['children']
        news_list = []

        for item in res:
            news_list.append({'headline': item['data']['title'], 'link': item['data']['url'], 'source':"reddit"})
        return news_list

    else:
        return list()

def newsAPI(q:str = None):

    if (q != None):
        res = requests.get(f"https://newsapi.org/v2/everything?q={q}&from=2021-10-10&sortBy=popularity&apiKey={news_api['key']}")
    else:
        res = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api['key']}")

    if (res.status_code == 200):
        articles = res.json()['articles']

        news_list = []

        for item in articles:
            news_list.append({'headline': item['title'], 'link': item['url'], 'source': "newsAPI"})
        
        return news_list

    else:
        return list()


@app.get('/news')
async def breaking_news(query:Optional[str] = Query(None)):
    NotCalled = True

    if ((query != None) and (query not in cache)):
        news_api = newsAPI(q=query)
        reddit_api = redditAPI(q=query)

        cache[query] = list(itertools.chain(news_api, reddit_api))

        return json.dumps(cache[query])
    

    if ((query == None) and (NotCalled)):
        news_api = newsAPI(q=query)
        reddit_api = redditAPI(q=query)
        cache['list'] = list(itertools.chain(news_api, reddit_api))
        NotCalled = False

    return json.dumps(cache['list'])
   
