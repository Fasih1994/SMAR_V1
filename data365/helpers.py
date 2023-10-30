import os
import requests
import json
import pandas as pd

def get_data(url:str = None, keywords: str = None, page:str = None, params: dict=None):
    
    try:
        
        if page: 
            params['cursor'] = page
        if keywords:
            params['keywords'] = keywords

        r = requests.get(url=url, params=params)

        if r.status_code==200:
            data = r.json()['data']
            if len(data['items'])>0:
                return data
            print(r.json())
            return None
        else:
            print(f'error occured for {keywords} on {url}')
            print(r.status_code, r.json()['error']['message'], sep='\n')
            raise Exception
    except Exception as e:
        print(str(e))

def join_list(array:list = None)-> str:
    array = [item for item in array if isinstance(item, str)]
    if len(array)>0:
        joined = "--|--".join(array)
        return joined
    return ""

def transform_data(data:dict=None)->pd.DataFrame:
    data_dict = {}

    for item in data['items']:
        for k, v in item.items():
            if k == 'attached_videos' and v != None:
                v = v[0]['url']
            if isinstance(v,list):
                if k in data_dict:
                    data_dict[k].append(join_list(v))
                else:
                    data_dict[k] = [join_list(v)] 
            else:
                if k in data_dict:
                    data_dict[k].append(v)
                else:
                    data_dict[k] = [v]

    df = pd.DataFrame(data_dict)
    return df