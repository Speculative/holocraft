import pdb
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterator, List, Literal, Optional, Union

import googleapiclient.discovery as api  # type: ignore
import requests
from dataclasses_json import DataClassJsonMixin, config
from dateutil.parser import isoparse
from marshmallow import fields

_total_quota_usage = 0
_total_html_fetches = 0


@dataclass
class YouTubeResponsePageInfo:
    totalResults: int
    resultsPerPage: int


@dataclass
class YouTubeResponseCommon:
    pageInfo: YouTubeResponsePageInfo
    nextPageToken: Optional[str] = None
    prevPageToken: Optional[str] = None


@dataclass
class YouTubeChannelRelatedPlaylists:
    uploads: str


@dataclass
class YouTubeChannelContentDetails:
    relatedPlaylists: YouTubeChannelRelatedPlaylists


@dataclass
class YouTubeThumbnail:
    url: str
    width: int
    height: int


@dataclass
class YouTubeChannelSnippet:
    title: str
    thumbnails: Dict[str, YouTubeThumbnail]


@dataclass
class YouTubeChannelResource:
    contentDetails: Optional[YouTubeChannelContentDetails] = None
    snippet: Optional[YouTubeChannelSnippet] = None


@dataclass
class YouTubeChannelListResponse(DataClassJsonMixin, YouTubeResponseCommon):
    items: List[YouTubeChannelResource] = field(default_factory=list)


def get_upload_playlist_id(youtube: api.Resource, channel_id: str):
    global _total_quota_usage
    _total_quota_usage += 1

    request = youtube.channels().list(part="contentDetails", id=channel_id)
    response = YouTubeChannelListResponse.from_dict(request.execute())
    if response.pageInfo.totalResults == 0 or response.items[0].contentDetails is None:
        return None

    return response.items[0].contentDetails.relatedPlaylists.uploads


def get_channel_picture(youtube: api.Resource, channel_id: str):
    global _total_quota_usage
    _total_quota_usage += 1

    request = youtube.channels().list(part="snippet", id=channel_id)
    response = YouTubeChannelListResponse.from_dict(request.execute())
    if response.pageInfo.totalResults == 0 or response.items[0].snippet is None:
        return None

    thumbnails = response.items[0].snippet.thumbnails
    if "default" in thumbnails:
        return thumbnails["default"].url
    return None


@dataclass
class YouTubePlaylistItemContentDetails:
    videoId: str
    videoPublishedAt: datetime = field(
        metadata=config(
            decoder=isoparse,
            mm_field=fields.DateTime(format="iso"),
        )
    )


@dataclass
class YouTubePlaylistItemSnippet:
    title: str
    description: str
    channelTitle: str
    thumbnails: Dict[str, YouTubeThumbnail]


@dataclass
class YouTubePlaylistItemResource:
    contentDetails: YouTubePlaylistItemContentDetails
    snippet: YouTubePlaylistItemSnippet


@dataclass
class YouTubePlaylistListResponse(DataClassJsonMixin, YouTubeResponseCommon):
    items: List[YouTubePlaylistItemResource] = field(default_factory=list)


@dataclass
class YouTubeVideoContentDetails:
    duration: str


@dataclass
class YouTubeVideoSnippet:
    title: str
    description: str
    channelTitle: str
    thumbnails: Dict[str, YouTubeThumbnail]
    publishedAt: datetime = field(
        metadata=config(
            decoder=isoparse,
            mm_field=fields.DateTime(format="iso"),
        )
    )


@dataclass
class YouTubeVideoItemResource:
    id: str
    contentDetails: YouTubeVideoContentDetails
    snippet: YouTubeVideoSnippet


@dataclass
class YouTubeVideoListResponse(DataClassJsonMixin, YouTubeResponseCommon):
    items: List[YouTubeVideoItemResource] = field(default_factory=list)


def playlist_videos(
    youtube: api.Resource, playlist_id: str
) -> Iterator[YouTubeVideoItemResource]:
    global _total_quota_usage

    page_token = None
    while True:
        _total_quota_usage += 1
        playlist_request = youtube.playlistItems().list(
            part="contentDetails,snippet",
            maxResults=50,
            playlistId=playlist_id,
            pageToken=page_token,
        )
        raw_playlist_response = playlist_request.execute()
        playlist_response = YouTubePlaylistListResponse.from_dict(raw_playlist_response)

        video_request = youtube.videos().list(
            id=",".join(
                [
                    item.contentDetails.videoId
                    for item in playlist_response.items
                    if item.snippet.title not in ["Deleted video", "Private video"]
                ]
            ),
            part="contentDetails,snippet",
        )
        raw_response = video_request.execute()
        video_response = YouTubeVideoListResponse.from_dict(raw_response)

        for playlist_item in video_response.items:
            yield playlist_item

        if playlist_response.nextPageToken is None:
            break
        page_token = playlist_response.nextPageToken


def is_minecraft_video(video: YouTubeVideoItemResource):
    global _total_html_fetches

    # If we see minecraft in the video title we can save some time
    normalized_title = video.snippet.title.lower()
    if any(indicator in normalized_title for indicator in ["minecraft", "マイクラ"]):
        return True

    # Otherwise we try the weird strategy of finding the explicit string "Minecraft" with quotes
    # which matches the a javascript payload on the video page for the meta game info block.
    # This will probably break some day in the distant future.
    #
    # Why would YouTube add this useful metadata to the API? Don't be ridiculous.
    _total_html_fetches += 1
    video_page = requests.get(f"https://youtube.com/watch?v={video.id}")
    return re.search(r"\"simpleText\":\"Minecraft\"", video_page.text) is not None


def get_quota_usage():
    return _total_quota_usage


def get_html_fetches():
    return _total_html_fetches
