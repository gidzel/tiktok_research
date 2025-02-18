import requests
from urllib.parse import urljoin
from datetime import datetime, timedelta
from .tiktok_research_enums import *
from bs4 import BeautifulSoup
import json
import os
import time

class TikTokResearch():
    def __init__(self, client_key, client_secret, deltadays=1):
        self.session = requests.Session()
        self.base_address = 'https://open.tiktokapis.com/v2/'
        self.client_key = client_key
        self.client_secret = client_secret
        self.access_token = ''
        self.token_type = ''
        self.expires_in = 0
        self.expire_ts = 0
        self.get_token()
        # 1 day timedelta as workaround for TTAPI bug. Max 30 days possible
        # see: https://stackoverflow.com/questions/79023955/tiktok-query-videos-research-api-getting-search-id-is-invalid-or-expired
        self.time_delta = timedelta(days=deltadays)
        self.max_count = 100

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
            self.expire_ts =  int(time.time()) + self.expires_in
        else:
            raise Exception(f"Failed to obtain access token: {res.text}")

    def api_request(self, node:ApiNodes, query, fields):
        if int(time.time()) > self.expire_ts:
            print("token expired - getting new one")
            self.get_token()
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
                raise Exception(f"{error['code']}: {error['message']}\nLOG ID: {error['log_id']}")
            return res.json().get('data', {})
        elif res.status_code == 400:
            error = res.json().get('error', {})
            raise Exception(f"{error['code']}: {error['message']}\nLOG ID: {error['log_id']}")
        else:
            return None

    def get_user(self, username: str, fields:list[UserFields]=UserFields.all()):
        if username == None:
            return None
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
        fields = ','.join([f.value for f in fields])
        videos = []
        temp_start_date = start_date
        temp_end_date = start_date + self.time_delta
        if temp_end_date > end_date:
            temp_end_date = end_date

        while(temp_start_date < end_date):
            cursor = 0
            search_id = ""
            has_more = True
            main_query = {}
            res = {}
            count_none_res = 0
            while has_more:
                try:
                    print(temp_start_date.strftime("%Y%m%d"), temp_end_date.strftime("%Y%m%d"), cursor, search_id)
                    res = self.video_query(
                        query = {
                            "query": query,
                            "max_count": self.max_count,
                            "start_date": temp_start_date.strftime("%Y%m%d"),
                            "end_date": temp_end_date.strftime("%Y%m%d"),
                            "cursor": cursor,
                            'search_id': search_id
                        },
                        fields=fields
                    )
                    if res == None: #some request dont return result
                        count_none_res += 1
                        if count_none_res < 10:#sometimes the api hangs, but when there is no result its the same pattern
                            time.sleep(2)
                            continue
                        else:
                            break
                    count_none_res = 0
                except Exception as e:
                    print(e)
                    print("try again")
                    time.sleep(2)
                    continue #handle the bug "Search Id XXXX is invalid or expired"

                cursor = res.get('cursor', cursor)
                search_id = res.get('search_id', search_id)
                has_more = res.get('has_more', True)
                videos += res.get('videos', [])

            temp_start_date += self.time_delta
            temp_end_date += self.time_delta
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
        query['max_count'] = self.max_count
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
                if res == None:
                    break
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
        print(tt)
        cookies = tt.cookies
        soup = BeautifulSoup(tt.text, "html.parser")
        tt_video_url = ''
        tt_script = soup.find('script', attrs={'id':"__UNIVERSAL_DATA_FOR_REHYDRATION__"})
        if tt_script != None:
            tt_json = json.loads(tt_script.string)
            tt_video_url = (tt_json.get("__DEFAULT_SCOPE__", {}).get('webapp.video-detail', {}).get(
                'itemInfo', {}).get('itemStruct', {}).get('video', {}).get('playAddr', ''))
        else:
            print("try alternative")
            tt_script = soup.find('script', attrs={'id':"SIGI_STATE"})
            if tt_script == None:
                print(tt.text)
                return
            tt_json = json.loads(tt_script.string)
            print(tt_json)
            tt_video_url = tt_json.get('ItemModule', {}).get(video_id, {}).get('video', {}).get('downloadAddr', '')
        if tt_video_url == '':
            print("download_video: Found no video URL for", username, str(video_id))
            return None
        try:
            tt_video = requests.get(
                tt_video_url, 
                allow_redirects=True, 
                headers=headers,
                cookies=cookies
                )
        except Exception as e:
            print(e)
            return None
        video_fn = os.path.join(path, username+'_'+str(video_id)+'.mp4')
        with open(video_fn, 'wb') as fn:
            fn.write(tt_video.content)
        return video_fn

    def download_avatar(self, user, path):
        if ('display_name' in user) and ('avatar_url' in user):
            headers={'Authorization': 'Bearer '+self.access_token,}
            try:
                avatar = requests.get(
                    user['avatar_url'], 
                    allow_redirects=True,
                    headers=headers
                )
            except Exception as e:
                print(e)
                return None
            avatar_path = os.path.join(path, 'avatar_'+user['display_name']+'.jpg')
            with open(avatar_path, 'wb') as fn:
                fn.write(avatar.content)
            return avatar_path
        else:
            return None