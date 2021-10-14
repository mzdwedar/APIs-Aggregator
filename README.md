# APIs-Aggregator

## Requirements
FastAPI
Python 3.9

## To Run:
uvicorn main:app -reload

## Routes
/news
-> list the news from (newsAPI and redditAPI)

/news/?query=keyword
-> return news that are related to the keyword
