import requests
from urllib.parse import urljoin
from datetime import datetime, timedelta
from .tiktok_research_enums import *
from bs4 import BeautifulSoup
import json
import os

class TikTokResearch():
    def __init__(self, client_key, client_secret):
        self.session = requests.Session()
        self.base_address = 'https://open.tiktokapis.com/v2/'
        self.client_key = client_key
        self.client_secret = client_secret
        self.access_token = ''
        self.token_type = ''
        self.expires_in = 0
        self.get_token()

    def get_token(self):
        res = self.session.post(
            url = urljoin(self.base_address, ApiNodes.token.value), 
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }, 
            data={
                'client_key': self.client_key,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials',
            }
        )

        if res.status_code == 200:
            res_obj = res.json()
            self.access_token = res_obj['access_token']
            self.token_type = res_obj['token_type']
            self.expires_in = res_obj['expires_in']
        else:
            raise Exception(f"Failed to obtain access token: {res.text}")

    def api_request(self, node:ApiNodes, query, fields):
        res = self.session.post(
            url = urljoin(self.base_address, node.value), 
            headers={
                'Authorization': 'Bearer '+self.access_token, 
                'Content-Type': 'application/json'
            }, 
            json=query, 
            params={
                'fields': fields
            }
        )
        if res.status_code == 200:
            error = res.json().get('error', {})
            if error['code'] != 'ok':
                raise Exception(f"{error['code']}: {error['message']}")
            return res.json().get('data', {})
        elif res.status_code == 400:
            error = res.json().get('error', {})
            raise Exception(f"{error['code']}: {error['message']}")
        else:
            return None

    def get_user(self, username: str, fields:list[UserFields]=UserFields.all()):
        fields = ','.join([f.value for f in fields])
        return self.api_request(
            node=ApiNodes.userinfo,
            query={
                "username": username
            },
            fields=fields
        )

    def video_query(self, query, fields:list[VideoFields]):
        return self.api_request(node=ApiNodes.video, query=query, fields=fields)

    def get_multiple_videos(
        self,
        query,
        start_date:datetime = datetime(2018, 8, 2), 
        end_date:datetime = datetime.now(), 
        fields:list[VideoFields]=VideoFields.all()
    ):
        td = timedelta(days=30)
        fields = ','.join([f.value for f in fields])
        videos = []
        temp_start_date = start_date
        temp_end_date = start_date+td

        while(temp_start_date < end_date):
            cursor = 0
            search_id = ""
            has_more = True
            while has_more:
                try:
                    res = self.video_query(
                        query={
                            "query": query,
                            "max_count": 100,
                            "start_date": temp_start_date.strftime("%Y%m%d"),
                            "end_date": temp_end_date.strftime("%Y%m%d"),
                            "cursor": cursor,
                            "search_id": search_id
                        },
                        fields=fields
                    )
                    cursor = res['cursor']
                    search_id = res['search_id']
                    has_more = res['has_more']
                    videos += res['videos']
                except Exception as e:
                    print(e)
                    return videos
            temp_start_date += td
            temp_end_date += td
            if temp_end_date > end_date:
                temp_end_date = end_date
        return videos

    def get_videos_by_usernames(
        self,
        usernames:list[str], 
        start_date:datetime = datetime(2018, 8, 2), 
        end_date:datetime = datetime.now(), 
        fields:list[VideoFields]=VideoFields.all()
    ):
        query = {
            "and": [{
                "operation": "IN", 
                "field_name": "username", 
                "field_values": usernames
            }]
        }
        return self.get_multiple_videos(
            query,
            start_date, 
            end_date, 
            fields
        )

    def get_videos_by_hashtags(
        self,
        hashtags:list[str], 
        region_codes: list[RegionCodes],
        start_date:datetime = datetime(2018, 8, 2), 
        end_date:datetime = datetime.now(), 
        fields:list[VideoFields]=VideoFields.all()
    ):
        region_codes = [rc.value for rc in region_codes]
        query =  {
            "and": [
                {
                    "operation": "IN", 
                    "field_name": "hashtag_name",
                    "field_values": hashtags
                },
                {
                    "operation": "IN", 
                    "field_name": "region_code", 
                    "field_values": region_codes
                }
            ]
        }
        return self.get_multiple_videos(
            query,
            start_date, 
            end_date, 
            fields
        )

    def get_videos_by_music_ids(
        self,
        music_ids:list[int], 
        start_date:datetime = datetime(2018, 8, 2), 
        end_date:datetime = datetime.now(), 
        fields:list[VideoFields]=VideoFields.all()
    ):
        query = {
            "and": [{
            "operation": "IN", 
            "field_name": "music_id", 
            "field_values": music_ids
            }]
        }
        return self.get_multiple_videos(
            query,
            start_date, 
            end_date, 
            fields
        )

    def get_paginated_items(
        self, 
        node:ApiNodes,
        query,
        item_name: str,
        fields = None,
    ):
        query['max_count'] = 100
        query['cursor'] = 0
        items = []
        has_more = True
        while(has_more):
            try:
                res = self.api_request(
                    node = node,
                    query = query,
                    fields = fields
                )
                query['cursor'] = res['cursor']
                has_more = res['has_more']
                items += res[item_name]
            except Exception as e:
                print(e)
                return items
        return items

        
    def get_comments(
        self, 
        video_id:int, 
        fields:list[CommentFields]=CommentFields.all()
    ):
        fields = ','.join([f.value for f in fields])
        return self.get_paginated_items(
            node=ApiNodes.comments,
            query={
                'video_id': video_id
            },
            fields=fields,
            item_name='comments'
        )

    def get_user_liked_videos(
        self,
        username: str,
        fields:list[VideoSmallFields]=VideoSmallFields.all()
    ):
        fields = ','.join([f.value for f in fields])
        return self.get_paginated_items(
            node=ApiNodes.userlikes,
            query={
                'username': username
            },
            item_name='user_liked_videos',
            fields=fields
        )
            
    def get_user_pinned_videos(
        self,
        username: str,
        fields:list[VideoSmallFields]=VideoSmallFields.all()
    ):
        fields = ','.join([f.value for f in fields])
        return self.api_request(
            node=ApiNodes.userpins, 
            query={
                'username': username
            }, 
            fields=fields
        )['pinned_videos_list']
            
    def get_user_followers(
        self,
        username: str
    ):
        return self.get_paginated_items(
            node=ApiNodes.userfollowers,
            query={
                'username': username
            },
            item_name='user_followers',
        )

    def get_user_following(
        self,
        username: str
    ):
        return self.get_paginated_items(
            node=ApiNodes.userfollowing,
            query={
                'username': username
            },
            item_name='user_following',
        )

    def get_user_reposts(
        self,
        username: str,
        fields:list[VideoSmallFields]=VideoSmallFields.all()
    ):
        fields = ','.join([f.value for f in fields])
        return self.get_paginated_items(
            node=ApiNodes.userreposts,
            query={
                'username': username
            },
            item_name='user_reposted_videos',
            fields=fields
        )

    def get_playlist(
        self,
        playlist_id: int
    ):
        return self.api_request(
            node=ApiNodes.playlist,
            query={
                'playlist_id': playlist_id
            }
        )

    def download_video(self, username:str, video_id:int, path: str = '.'):
        url = 'https://www.tiktok.com/@'+username+"/video/"+str(video_id)
        headers={'Authorization': 'Bearer '+self.access_token,}
        tt = self.session.get(url, headers=headers)
        cookies = tt.cookies
        soup = BeautifulSoup(tt.text, "html.parser")
        tt_video_url = ''
        tt_script = soup.find('script', attrs={'id':"__UNIVERSAL_DATA_FOR_REHYDRATION__"})
        if tt_script != None:
            tt_json = json.loads(tt_script.string)
            tt_video_url = (tt_json["__DEFAULT_SCOPE__"]['webapp.video-detail']
                ['itemInfo']['itemStruct']['video']['playAddr'])
        else:
            tt_script = soup.find('script', attrs={'id':"SIGI_STATE"})
            tt_json = json.loads(tt_script.string)
            tt_video_url = tt_json['ItemModule'][video_id]['video']['downloadAddr']
        
        tt_video = requests.get(
            tt_video_url, 
            allow_redirects=True, 
            headers=headers,
            cookies=cookies
            )
        video_fn = os.path.join(path, username+'_'+str(video_id)+'.mp4')
        with open(video_fn, 'wb') as fn:
            fn.write(tt_video.content)
        return video_fn
