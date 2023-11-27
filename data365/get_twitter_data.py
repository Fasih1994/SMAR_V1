import os
import time
from data365.helpers import get_data, transform_data
from dotenv import load_dotenv
import requests
import pandas as pd
from typing import Literal
from datetime import datetime

from utils import get_engine, get_logger

load_dotenv()

logger = get_logger("SMAR")

base_query_param = {
    'access_token': os.environ['DATA365_KEY'],
    'max_page_size': 100,
    'order_by': "date_asc"
}

sql_server_engine = get_engine()

def update_existing_records(sql_server_engine, df, posts: bool = True):
    # select table
    if posts:
        table = 'twitter_posts'
    else:
        table = 'twitter_comments'


    if not df.empty:
        # Create a list of update statements for each column excluding 'id', 'sentiment', and 'tone'
        update_statements = [f"target.{col} = source.{col}" for col in df.columns if col not in ['id', 'sentiment', 'tone', 'tweet_insert_timestamp']]

        # SQL query to perform an upsert using MERGE
        merge_query = f"""
            MERGE INTO SMAR.dbo.{table} AS target
            USING (VALUES {df.to_records(index=False)}) AS source ({', '.join(df.columns)})
            ON target.id = source.id
            WHEN MATCHED THEN
                UPDATE SET
                    {', '.join(update_statements)},
                    target.tweet_insert_timestamp = source.tweet_insert_timestamp
            WHEN NOT MATCHED THEN
                INSERT ({', '.join(df.columns)})
                VALUES ({', '.join(['source.' + col for col in df.columns])});
        """

        try:
            with sql_server_engine.connect() as connection:
                connection.execute(merge_query)
            logger.info("Existing records updated in SQL Server.")
        except Exception as e:
            logger.error(f"Error updating existing records in SQL Server: {e}")
    else:
        logger.info("No existing records to update.")


# Rest of your code...


def get_twitter_posts(key_word:str = None):
    url = "https://api.data365.co/v1.1/twitter/search/post/posts"
    update_url = "https://api.data365.co/v1.1/twitter/search/post/update"
    status_url = "https://api.data365.co/v1.1/twitter/search/post/update"
    logger.info(f"Updating tasks for {key_word}")
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
            failed = True
        if not finished:
            time.sleep(2)
    logger.info(f"Finished tasks for {key_word}")


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
                data_available = False # remove this to get all data
            else:
                data_available = False
        else:
            data_available = False

    if data_dict['items']!= []:
        df = transform_data(data_dict)
        df['term'] = key_word
        df['sentiment'] = 'unknown'
        df['tone'] = 'unknown'

        # Add tweet_insert_timestamp column with the current timestamp
        df['tweet_insert_timestamp'] = datetime.now()

        logger.info(f"Data is {df.head()}")
        write_path = f"data/Twitter/twitter_posts_for_{'-'.join(key_word.split())}.csv"
        df.to_csv(write_path, index=False)
        df.to_sql('twitter_posts', sql_server_engine, if_exists='append', index=False)

        # update_existing_records(sql_server_engine, df)
        return write_path
    return ""

def get_twitter_comments(path: str=None, key_word:str = None):
    update_url = "https://api.data365.co/v1.1/twitter/profile/{profile_id}/{section}/posts/{post_id}/update"
    url = "https://api.data365.co/v1.1/twitter/profile/{profile_id}/{section}/posts/{post_id}/replies"
    ids = []
    params = {
        'access_token': os.environ['DATA365_KEY'],
    }
    logger.info(f"getting comments for {key_word}")

    tweets = pd.read_csv(path)
    tweets_with_reply = tweets[tweets['reply_count'] >= 1].head(50)
    logger.info(f"data is {tweets_with_reply.head()}")
    data = {'items': []}
    # data_not_extracted = True
    # while data_not_extracted:
    for i, id in zip(tweets_with_reply.index,tweets_with_reply['id']):
        new_update_url = update_url.format(post_id=tweets_with_reply.loc[i,'id'], section='feed', profile_id=tweets_with_reply.loc[i,'author_id'])
        update_res = requests.post(new_update_url, params=params)

    ids = tweets_with_reply.index.tolist()
    while len(ids)>0:
        for i in ids:
            new_update_url = update_url.format(post_id=tweets_with_reply.loc[i,'id'], section='feed', profile_id=tweets_with_reply.loc[i,'author_id'])
            r = requests.get(new_update_url, params=params)
            if r.json()['data']['status'] == 'finished':
                ids.remove(i)
                new_url = url.format(post_id=tweets_with_reply.loc[i,'id'], section='feed', profile_id=tweets_with_reply.loc[i,'author_id'])
                r = requests.get(url=new_url, params=params)
                items = r.json()['data']['items']
                logger.info(f"GET for comment id: {tweets_with_reply.loc[i,'id']} finished! \n {items}")
                data['items'].extend(items)
                items = None
            elif r.json()['data']['status'] == 'failed':
                ids.remove(i)
                logger.warning(f"get for comment id: {tweets_with_reply.loc[i,'id']} failed!")

    logger.info(f"GET for comments Completed!")
    if data['items'] != []:
        # data_not_extracted = False
        comments = transform_data(data)
        comments['term'] = key_word
        comments['sentiment'] = 'unknown'
        comments['tone'] = 'unknown'
        # Add tweet_insert_timestamp column with the current timestamp
        comments['tweet_insert_timestamp'] = datetime.now()

        logger.info(f"comments are {comments.head()}")
        # comments_to_insert = update_existing_records(sql_server_engine, comments, posts=False)
        comments.to_sql('twitter_comments', sql_server_engine, if_exists='append', index=False)
        logger.info(f"comments are written to db for {key_word}")


def get_twitter_data_from_db(
    terms:list[str] = None,
    table: Literal['comments','posts'] = 'posts'
    ) -> pd.DataFrame:
    if terms == []:
        return None

    if table=='posts':
        sql = f"""
        SELECT top 100 author_username --, created_time, view_count, text, tone, sentiment , geo_lat, geo_lon
        FROM twitter_posts
        WHERE term in ('{"', '".join(terms)}');
        """
    elif table=='comments':
        sql = f"""
        SELECT top 100 author_username , created_time, view_count, text, tone, sentiment , geo_lat, geo_lon
        FROM twitter_comments
        WHERE term in ('{"', '".join(terms)}');
        """
    # print(sql)

    df = pd.read_sql_query(sql, sql_server_engine)
    df.fillna('unavailable', inplace=True)
    return df
