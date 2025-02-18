from peewee import *

db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = TextField(unique=True)
    displayname = TextField(null=True) #This is the user's profile name that is found under the username.
    following_cnt = IntegerField(null=True) #This is the number of people that a public user follows.
    follower_cnt = IntegerField(null=True) #This is the total number of followers that follow the user.
    like_cnt = IntegerField(null=True) #This is the total number of likes accumulated by the user.
    video_cnt = IntegerField(null=True) #This is the total number of videos that the user has posted on their TikTok account.
    bio = TextField(null=True) #This is the description in the bio of the user. If the user does not have a description, this will be returned blank.
    bio_url = TextField(null=True) #The public URL in the user's bio will be shared here.
    avatar_url = TextField(null=True) #This is the URL of the user's profile picture.
    avatar_path = TextField(null=True)
    is_verified = BooleanField(null=True) #This returns the information on whether the user has been verified. All verified users will have "blue tick" next to their username. If the user has a blue tick, this variable will return a "true" in the response.

class Region(BaseModel):
    name=CharField(unique=True, max_length=2) #A two digit code for the country where the video creator registered their account.
    desc=TextField(null=True)

class Video(BaseModel):
    item_id = BigIntegerField(unique=True)#The unique identifier of the TikTok video. This is also called "item_id" or "video_id".
    create_time = DateTimeField(null=True) #This is the time when the video was created.
    user = ForeignKeyField(User, backref='videos', null=True)#This is the username of the video creator.
    region = ForeignKeyField(Region, backref='videos', null=True) 
    desc = TextField(null=True)#This is the description of the video.
    music_id = BigIntegerField(null=True)#This is the music_id used in the video.
    like_cnt = IntegerField(null=True)#The total number of likes on a TikTok video, created by users by clicking the “Heart” icon.
    comment_cnt = IntegerField(null=True)#This is the total number of comments posted on a video.
    share_cnt = IntegerField(null=True)#The total number of times a TikTok video has been shared by clicking the "Share" button with the video.
    view_cnt = IntegerField(null=True)#This is the total number of views for a video on TikTok.
    # video_id = BigIntegerField()#This is a unique video ID for each video posted on TikTok. This is a number that can be used to reconstruct the URL link to access the video.
    voice_to_text = TextField(null=True)#Voice to text and subtitles (for videos that have voice to text features on, show the texts already generated)
    is_stem_verified = BooleanField(null=True)#Whether the video has been verified as being high quality STEM content.
    duration = IntegerField(null=True)#The duration of the video in seconds.
    favorites_count = IntegerField(null=True)#The number of favorites a video receives.
    path = TextField(null=True)

    label_warn = BooleanField(default=False)
    label_content = TextField(default='')
    label_sink = BooleanField(default=False)
    label_type = IntegerField(default=0)
    label_vote = BooleanField(default=False)

class Hashtag(BaseModel):
    tt_id = BigIntegerField()#Returns the unique hashtag_ids for each hashtag.
    name = TextField(unique=True)
    desc = TextField(null=True)#Returns a description for a hashtag_name if one exists.

class HashtagOnVideo(BaseModel):
    hashtag = ForeignKeyField(Hashtag, backref='videos')
    video = ForeignKeyField(Video, backref='hashtags')#The list of hashtags used in the video.
    class Meta:
        primary_key = CompositeKey('hashtag', 'video')
    
class Effect(BaseModel):
    name = TextField()
    desc = TextField()

class EffectOnVideo(BaseModel):
    effect = ForeignKeyField(Effect, backref='videos')
    video = ForeignKeyField(Video, backref='effects')#The list of effects applied on the video.
    class Meta:
        primary_key = CompositeKey('video', 'effects')

class Comment(BaseModel):
    create_time = DateTimeField(null=True)#This is the time when the comment was posted on a video.
    tt_id = BigIntegerField(unique=True)#This is the unique comment ID for a comment posted on a video.
    like_cnt = IntegerField(default=0)#The total number of likes for a comment under a video, created by users by clicking the “Heart” icon.
    parent = ForeignKeyField('self', backref='childs', null=True)#This is the unique ID of the parent comment when the user responds to another user's comment. If the comment was directly entered for a video, this ID is the same as the Video ID.
    reply_cnt = IntegerField(default=0)#This is the total number of replies on a particular comment.
    text = TextField(null=True)#This is the actual text of the comment entered on a video. To protect the privacy of our users, other information is removed.
    video = ForeignKeyField(Video, backref='comments', null=True)#This is the video ID for which the comment was entered.

class UserOnUser(BaseModel):#Following
    following = ForeignKeyField(User, backref='follower')
    follower = ForeignKeyField(User, backref='following')
    class Meta:
        primary_key = CompositeKey('following', 'follower')

class UserOnVideo(BaseModel): #Tagging
    user = ForeignKeyField(User, backref='tagged_videos')
    video = ForeignKeyField(Video, backref='tagged_users')#Returns the other tagged users in a video.
    class Meta:
        primary_key = CompositeKey('user', 'video')

class Playlist(BaseModel):
    #id#The ID of the playlist that the video belongs to.
    name = TextField()

class VideoOnPlaylist(BaseModel):
    video = ForeignKeyField(Video, backref='playlists')
    playlist = ForeignKeyField(Playlist, backref='videos')
    class Meta:
        primary_key = CompositeKey('playlist', 'video')