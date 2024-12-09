
# TikTok Research Python Library

This library provides a Python interface for interacting with TikTok's official Research API. It allows developers to retrieve information on TikTok videos, comments, users, user likes, followers, following lists, reposts, and playlists.

## Features

- Query TikTok videos and retrieve metadata
- Fetch user details, followers, likes, and following lists
- Retrieve reposts and playlists data
- Authenticate using TikTok's API

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gidzel/tiktok_research.git
   cd tiktok_research
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Initialization

First, initialize the `TikTokResearch` class with your TikTok API credentials:

```python
from tiktok_research import TikTokResearch, VideoFields, UserFields, RegionCodes
from datetime import datetime

# Initialize the API client
ttr = TikTokResearch(client_key='your_client_key', client_secret='your_client_secret')
```

### Fields

Fields are the data fields you can obtain from the entities. See `tiktok_research_enums.py` for all options.

### Querying Videos

Retrieve information about videos:

**by usernames**
```python
videos = ttr.get_videos_by_usernames(
    usernames = ['dummy1', 'dummy2'],
    start_date = datetime(2023, 1, 1),
    end_date = datetime(2024, 10, 31),
    fields = VideoFields.all()
)
print(videos)
```

**by hashtags**
```python
videos = ttr.get_videos_by_hashtags(
    hashtags = ['foryoupage'],
    region_codes = [RegionCodes.germany, RegionCodes.austria],
    start_date = datetime(2024, 11, 20),
    end_date = datetime(2024, 11, 25),
    fields = VideoFields.all()
)
print(videos)
```

**by sounds**
```python
videos = ttr.get_videos_by_music_ids(
    music_ids = [1234567890, 2345678901],
    start_date = datetime(2024, 11, 20),
    end_date = datetime(2024, 11, 25),
    fields = VideoFields.all()
)
print(videos)
```

### Download Video

```python
path = ttr.download_video(
   username = 'dummy', 
   video_id = 1234567890,
   path = 'somedir'
)
print(path)
```

### Fetching User Details

```python
user = ttr.get_user(
   username = 'dummy',
   fields = UserFields.all()
)
print(user)
```

### Accessing User Followers and Following

```python
followers = ttr.get_user_followers(
    username = 'dummy'
)

following = ttr.get_user_following(
    username = 'dummy'
)

print(followers, following)
```

### Retrieving Comments

Fetch comments on a video:

```python
comments = ttr.get_comments(
    video_id = 1234567890,
    fields = CommentFields.all()
)
print(comments)
```

### Reposts

```python
reposts = ttr.get_user_reposts(
    username = 'dummy',
    fields = VideoSmallFields.all()
)
print(reposts)
```

### Pinned Videos

```python
pinned_videos = ttr.get_user_pinned_videos(
    username = 'dummy',
    fields = VideoSmallFields.all()
)
print(pinned_videos)
```

## Using the DB Wrapper
### Initialization
Import `TikTokResearchDb` and init it with your credentials and db-path, files-path
```python
from tiktok_research import TikTokResearchDb, VideoFields, UserFields, RegionCodes
from datetime import datetime

ttr = TikTokResearchDb(
    client_key='your_client_key', 
    client_secret='your_client_secret',
    db_path='path_to_your.sqlite',
    files_path='tiktok-videos'
)
```

### Example for scraping by hashtags

```python
ttr.scrape_videos_by_hashtag(
    hashtags=['fyp', 'cats'], 
    region_codes=[RegionCodes.germany],
    start_date=datetime(2024, 1, 1),
    end_date=datetime.now(),
    download=False # Flag for toggleing video and avatar download
)
```

## API Reference

For a detailed API reference, consult the official TikTok Research API documentation: [TikTok Research API Docs](https://developers.tiktok.com/doc/about-research-api).

## Contributing

We welcome contributions! Please submit a pull request or open an issue for any bugs or feature requests.

## License

This library is licensed under the MIT License.
