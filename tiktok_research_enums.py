from enum import Enum

class ExtendedEnum(Enum):
    @classmethod
    def all(self):
        return list(self)
    @classmethod
    def all_values(self):
        return list(map(lambda c: c, self))
    @classmethod
    def to_dict(self):
        return {c.name: c.value for c in self}
    @classmethod
    def to_rev_dict(self):
        return {c.value: c.name for c in self}

class ApiNodes(ExtendedEnum):
    token = 'oauth/token/'
    video = 'research/video/query/'
    comments = 'research/video/comment/list/'
    userinfo ='research/user/info/'
    userlikes = 'research/user/liked_videos/'
    userpins = 'research/user/pinned_videos/'
    userfollowers = 'research/user/followers/'
    userfollowing = 'research/user/following/'
    userreposts = 'research/user/reposted_videos/'
    playlist = 'research/playlist/info/'

class UserFields(ExtendedEnum):
    display_name = 'display_name'
    bio_description = 'bio_description'
    avatar_url = 'avatar_url'
    is_verified = 'is_verified'
    follower_count = 'follower_count'
    following_count = 'following_count'
    likes_count = 'likes_count'
    video_count = 'video_count'
    bio_url = 'bio_url'

class VideoSmallFields(ExtendedEnum):
    video_id = 'id'
    description = 'video_description'
    create_time = 'create_time'
    region_code = 'region_code'
    share_count = 'share_count'
    view_count = 'view_count'
    like_count = 'like_count'
    comment_count = 'comment_count'
    music_id = 'music_id'
    hashtag_names = 'hashtag_names'
    username = 'username'
    is_stem_verified = 'is_stem_verified'
    duration = 'video_duration'
    hashtag_info_list = 'hashtag_info_list'
    mention_list = 'video_mention_list'
    label = 'video_label'

class VideoFields(ExtendedEnum):
    video_id = 'id'
    description = 'video_description'
    create_time = 'create_time'
    region_code = 'region_code'
    share_count = 'share_count'
    view_count = 'view_count'
    like_count = 'like_count'
    # favourites_count = 'favourites_count'
    comment_count = 'comment_count'
    music_id = 'music_id'
    hashtag_names = 'hashtag_names'
    username = 'username'
    is_stem_verified = 'is_stem_verified'
    duration = 'video_duration'
    hashtag_info_list = 'hashtag_info_list'
    mention_list = 'video_mention_list'
    label = 'video_label'

    effect_ids = 'effect_ids'
    playlist_id = 'playlist_id'
    voice_to_text = 'voice_to_text'

class CommentFields(ExtendedEnum):
    comment_id = 'id'
    video_id = 'video_id'
    text = 'text'
    like_count = 'like_count'
    reply_count = 'reply_count'
    parent_comment_id = 'parent_comment_id'
    create_time = 'create_time'

class RegionCodes(ExtendedEnum):
    france = 'FR'
    italy = 'IT'
    usa = 'US'
    great_britain = 'GB'
    ukraine = 'UA'
    spain = 'ES'
    taiwan = 'TW'
    japan = 'JP'
    lithuania = 'LT'
    romania = 'RO'
    israel = 'IL'
    germany = 'DE'
    netherlands = 'NL'
    belgium = 'BE'
    hungaria = 'HU'
    portugal = 'PT'
    austria = 'AT'
    czech_republic = 'CZ'
    poland = 'PL'
    russia = 'RU'
    #'TH', 'MM', 'BD', 'NP', 'IQ', 'BR', 'KW', 'VN', 'AR', 'KZ', 
    #'TR', 'ID', 'PK', 'NG', 'KH', 'PH', 'EG', 'QA', 'MY'
    # 'DO', 'TZ', 'LK', 'NI', 'LB', 'IE', 'RS',
    # 'TN', 'LY', 'DZ', 'CG', 'GH', 'BJ', 'SN', 'SK', 'BY', 'LA',
    # 'JO', 'MA', 'SA', 'AF', 'EC', 'MX', 'BW'
    # 'GP', 'CM', 'HN', 'FI', 'GA', 'BN', 'SG', 'BO', 'GM', 'BG', 'SD', 'TT', 'OM', 'FO', 'MZ', 
    # 'ML', 'UG', 'RE', 'PY', 'GT', 'CI', 'SR', 'AO', 'AZ', 'LR', 'CD', 'HR', 'SV', 'MV', 'GY', 
    # 'BH', 'TG', 'SL', 'MK', 'KE', 'MT', 'MG', 'MR', 'PA', 'IS', 'LU', 'HT', 'TM', 'ZM', 'CR', 
    # 'NO', 'AL', 'ET', 'GW', 'AU', 'KR', 'UY', 'JM', 'DK', 'AE', 'MD', 'SE', 'MU', 'SO', 'CO', 
    # 'GR', 'UZ', 'CL', 'GE', 'CA'
    # 'ZA', 'AI', 'VE', 'KG', 'PE', 'CH', 'LV', 'PR', 'NZ', 'TL', 'BT', 'MN', 'FJ', 'SZ', 'VU', 
    # 'BF', 'TJ', 'BA', 'AM', 'TD', 'SI', 'CY', 'MW', 'EE', 'XK', 'ME', 'KY', 'YE', 'LS', 'ZW', 
    # 'MC', 'GN', 'BS', 'PF', 'NA', 'VI', 'BB', 'BZ', 'CW', 'PS', 'FM', 'PG', 'BI', 'AD', 'TV', 
    # 'GL', 'KM', 'AW', 'TC', 'CV', 'MO', 'VC', 'NE', 'WS', 'MP', 'DJ', 'RW', 'AG', 'GI', 'GQ', 
    # 'AS', 'AX', 'TO', 'KN', 'LC', 'NC', 'LI', 'SS', 'IR', 'SY', 'IM', 'SC', 'VG', 'SB', 'DM', 
    # 'KI', 'UM', 'SX', 'GD', 'MH', 'BQ', 'YT', 'ST', 'CF', 'BM', 'SM', 'PW', 'GU', 'HK', 'IN', 
    # 'CK', 'AQ', 'WF', 'JE', 'MQ', 'CN', 'GF', 'MS', 'GG', 'TK', 'FK', 'PM', 'NU', 'MF', 'ER', 
    # 'NF', 'VA', 'IO', 'SH', 'BL', 'CU', 'NR', 'TP', 'BV', 'EH', 'PN', 'TF', 
    