from .tiktok_research import TikTokResearch
from .tiktok_research_enums import *
from datetime import datetime
from .peewee_db_model import *
from pathlib import Path
import os

class TikTokResearchDb(TikTokResearch):
    def __init__(self, client_key, client_secret, db_path, files_path='.'):
        super().__init__(client_key, client_secret)
        self.db_path = db_path
        Path(files_path).mkdir(parents=True, exist_ok=True)
        self.files_path = files_path
        self.init_db()
    
    def init_db(self):
        self.db = db
        self.db.init(self.db_path)
        self.db.drop_tables([
            User, Video, 
            Region, 
            Hashtag, HashtagOnVideo, 
            UserOnVideo,
        ])
        self.db.create_tables([
            User, Video, 
            Region, 
            Hashtag, HashtagOnVideo, 
            # Effect, EffectOnVideo,
            # Comment,
            # UserOnUser,
            # UserOnVideo,
            # Playlist,
            # VideoOnPlaylist
        ])
    
    def db_create_region(self, region_code):
        if region_code == None:
            return None
        region_db, _ = Region.get_or_create(
            name = region_code,
            defaults = {
                'desc': RegionCodes.to_rev_dict().get(region_code, '')
            }
        )
        return region_db

    def db_create_hashtag(self, hashtag):
        hashtag_db, _ =  Hashtag.get_or_create(
            tt_id = hashtag['hashtag_id'],
            name = hashtag['hashtag_name'],
            defaults = {
                'desc': hashtag['hashtag_description'],
            }
        )
        return hashtag_db

    def db_create_hashtags(self, hashtag_info_list):
        if len(hashtag_info_list) == 0:
            return None
        return [self.db_create_hashtag(ht) for ht in hashtag_info_list]

    def db_create_user(self, user, download=False):
        if user.get('display_name', None) == None:
            return None

        avatar_path = None
        if download:
            avatar_path = self.download_avatar(user, self.files_path)

        user_db, _ = User.get_or_create(
            username = user['display_name'],
            defaults={
                'following_cnt': user.get('following_count', None),
                'follower_cnt': user.get('follower_count', None),
                'like_cnt': user.get('likes_count', None),
                'video_cnt': user.get('video_count', None),
                'bio': user.get('bio_description', None),
                'bio_url': user.get('bio_url', None),
                # 'displayname': user.get('display_name', None),
                'avatar_url': user.get('avatar_url', None),
                'avatar_path': avatar_path,
                'is_verified': user.get('is_verified', None),
            }
        )
        return user_db

    def db_create_video(self, video, download:bool=False):
        hashtags_db = self.db_create_hashtags(video.get('hashtag_info_list', []))
        region_db = self.db_create_region(video.get('region_code', None))
        user_db = None
        if download:
            user = self.get_user(video.get('username', None))
            user_db = self.db_create_user(
                user = user,
                download = download
            )
        else:
            user_db = self.db_create_user(
                user = {
                    'display_name': video.get('username', None)
                },
                download = download
            )
        video_labels = video.get('video_label', {})

        video_path = None
        if download and ('username' in video) and ('id' in video):
            video_path = self.download_video(
                username = video['username'],
                video_id = video['id'],
                path = self.files_path
            )

        video_db, _ = Video.get_or_create(
            item_id = video.get('id'),
            defaults = {
                'create_time': datetime.fromtimestamp(video.get('create_time', None)),
                'user': user_db,
                'region': region_db,
                'desc': video.get('video_description', None),
                'music_id': video.get('music_id', None),
                'like_cnt': video.get('like_count', None),
                'comment_cnt': video.get('comment_count', None),
                'share_cnt': video.get('share_count', None),
                'view_cnt': video.get('view_count', None),
                # 'video_id': video.get('', None),
                'voice_to_text': video.get('voice_to_text', None),
                'is_stem_verified': video.get('is_stem_verified', None),
                'duration': video.get('video_duration', None),
                #'favorites_count': video.get('', None),
                'label_warn': video_labels.get('warn', None),
                'label_content': video_labels.get('content', None),
                'label_sink': video_labels.get('sink', None),
                'label_type': video_labels.get('type', None),
                'label_vote': video_labels.get('vote', None),
                'path': video_path
            }
        )

        for hashtag_db in hashtags_db:#connect hashtags with video
            HashtagOnVideo.get_or_create(
                hashtag = hashtag_db,
                video = video_db
            )
        return video_db

    def db_create_videos(self, videos, download:bool=False):
        if len(videos) == 0:
            return None
        return [
            self.db_create_video(
                video=video, 
                download=download) 
                for video in videos
            ]

    def scrape_videos_by_hashtag(
        self, 
        hashtags:list[str], 
        region_codes:list[RegionCodes],
        start_date: datetime,
        end_date: datetime,
        download: bool=False
    ):
        videos = self.get_videos_by_hashtags(
            hashtags, 
            region_codes,
            start_date,
            end_date
        )
        print(f'L={len(videos)}')
        return self.db_create_videos(
            videos = videos, 
            download = download
        )

    def scrape_user_by_name(
        self,
        username: str,
        deep = False,
        download_avatar: bool = False,
        follower = False,
        following = False
    ):
        user = self.get_user(username=username)
        return self.db_create_user(user)
            
    def scrape_users_by_names(
        self,
        usernames: list[str],
        download_avatar: bool = False
    ):
        return [self.scrape_user_by_name(username, download_avatar) for username in usernames]    


