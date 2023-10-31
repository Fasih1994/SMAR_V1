import os
import time
from data365.helpers import get_data, transform_data
from dotenv import load_dotenv
import requests
import pandas as pd
from typing import Literal

from utils import get_engine

load_dotenv()

base_query_param = {
    'access_token': os.environ['DATA365_KEY'],
    'max_page_size': 100,
    'order_by': "date_asc"
}

sql_server_engine = get_engine()

def get_twitter_posts(key_word:str = None):
    url = "https://api.data365.co/v1.1/twitter/search/post/posts"
    update_url = "https://api.data365.co/v1.1/twitter/search/post/update"
    status_url = "https://api.data365.co/v1.1/twitter/search/post/update"

    # update task for keyword
    r = requests.post(
        update_url, 
        params={
            **base_query_param,
            "keywords": key_word
        }
    )

    # check taskh status
    finished = False
    failed = False
    while not finished:
        r = requests.get(status_url, params={
        **base_query_param,
        "keywords": key_word
        })
        if r.json()['data']['status'] == 'finished':
            finished = True
        elif r.json()['data']['status'] == 'failed':
            failed = False

        time.sleep(0.5)

    if failed: return None

    data_available = True
    page = 1
    cursor = None
    data_dict = {'items': []}
    while data_available:
        if cursor:
            data = get_data(url=url, keywords=key_word, page=cursor, params=base_query_param)
        else:
            data = get_data(url=url, keywords=key_word, params=base_query_param)
        
        if data:
            data_dict['items'].extend(data['items'])
            if data['page_info']['has_next_page']:
                cursor = data['page_info']['cursor']
                page += 1
            else:
                data_available = False
        else:
            data_available = False
            
    if data_dict['items']!= []:
        df = transform_data(data_dict) 
        df['term'] = key_word
        df['sentiment'] = 'unknown'
        df['tone'] = 'unknown'
        write_path = f"data/Twitter/twitter_posts_for_{'-'.join(key_word.split())}.csv"
        df.to_csv(write_path, index=False)
        df.to_sql('twitter_posts', sql_server_engine, if_exists='append' )
    
    return write_path

def get_twitter_comments(path: str=None, key_word:str = None):
    update_url = "https://api.data365.co/v1.1/twitter/profile/{profile_id}/{section}/posts/{post_id}/update"
    url = "https://api.data365.co/v1.1/twitter/profile/{profile_id}/{section}/posts/{post_id}/replies"
    ids = []
    params = {
        'access_token': os.environ['DATA365_KEY'],
    }

    tweets = pd.read_csv(path)
    tweets_with_reply = tweets[tweets['reply_count'] >= 1]
    data = {'items': []}
    data_not_extracted = True
    while data_not_extracted:
        for i, id in zip(tweets_with_reply.index,tweets_with_reply['id']):
            new_update_url = update_url.format(post_id=tweets_with_reply.loc[i,'id'], section='feed', profile_id=tweets_with_reply.loc[i,'author_id'])
            update_res = requests.post(new_update_url, params=params)
        time.sleep(0.2)
        for i, id in zip(tweets_with_reply.index,tweets_with_reply['id']):
            new_url = url.format(post_id=tweets_with_reply.loc[i,'id'], section='feed', profile_id=tweets_with_reply.loc[i,'author_id'])
            r = requests.get(url=new_url, params=params)
            data['items'].extend(r.json()['data']['items'])
            
        if data['items'] != []:
            data_not_extracted = False
            comments = transform_data(data)
            comments['term'] = key_word
            comments['sentiment'] = 'unknown'
            comments['tone'] = 'unknown'
            # write_path = f"data/Twitter/twitter_comments_for_{'-'.join(key_word.split())}.csv"
            # comments.to_csv(write_path, index=False)
            comments.to_sql('twitter_comments', sql_server_engine, if_exists='append' )
            
def get_twitter_data_from_db(
    terms:list[str] = None, 
    table: Literal['comments','posts'] = 'posts'
    ) -> pd.DataFrame:
    if terms == []:
        return None
    
    if table=='posts':
        sql = f"""
        SELECT * FROM twitter_posts 
        WHERE term in ('{"', '".join(terms)}');
        """
    elif table=='comments':
        sql = f"""
        SELECT * FROM twitter_comments 
        WHERE term in ('{"', '".join(terms)}');
        """
    # print(sql)
        
    df = pd.read_sql_query(sql, sql_server_engine)
    return df
