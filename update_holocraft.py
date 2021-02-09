import json
import sys
import re
import requests
import googleapiclient.discovery as api  # type: ignore
from itertools import chain
from typing import Dict, List, Set, Optional
from timeit import timeit
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, config
from datetime import datetime
from marshmallow import fields
from dateutil.parser import isoparse

DATAFILE_PATH = "docs/data/holocraft.json"
total_quota_usage = 0
total_html_fetches = 0


@dataclass
class HolocraftStream:
    # Member Channel ID whose source stream this is
    member: str
    # When the stream was published
    published_at: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )


@dataclass
class HolocraftClip:
    # Video IDs of source streams
    source_streams: List[str]


@dataclass
class HolocraftData(DataClassJsonMixin):
    # Member Name -> Channel ID
    members: Dict[str, str] = field(default_factory=dict)
    # [Clipper Channel ID]
    clippers: List[str] = field(default_factory=list)
    # Channel ID -> Upload Playlist ID
    upload_playlists: Dict[str, str] = field(default_factory=dict)
    # Channel ID -> Video ID
    seen_videos: Dict[str, Set[str]] = field(
        default_factory=dict,
        # We only want changes to show up in these sets when their membership changes,
        # so we sort them to get a more stable serialization output
        metadata=config(encoder=lambda d: {k: sorted(v) for k, v in d.items()}),
    )
    # Video ID -> HolocraftStream
    craft_streams: Dict[str, HolocraftStream] = field(default_factory=dict)
    # Video ID -> [Source Stream IDs]
    craft_clips: Dict[str, HolocraftClip] = field(default_factory=dict)


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
class YouTubeChannelResource:
    contentDetails: YouTubeChannelContentDetails


@dataclass
class YouTubeChannelListResponse(DataClassJsonMixin, YouTubeResponseCommon):
    items: List[YouTubeChannelResource] = field(default_factory=list)


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


@dataclass
class YouTubePlaylistItemResource:
    contentDetails: YouTubePlaylistItemContentDetails
    snippet: YouTubePlaylistItemSnippet


@dataclass
class YouTubePlaylistListResponse(DataClassJsonMixin, YouTubeResponseCommon):
    items: List[YouTubePlaylistItemResource] = field(default_factory=list)


def get_upload_playlist_id(youtube: api.Resource, channel_id: str):
    global total_quota_usage
    total_quota_usage += 1

    request = youtube.channels().list(part="contentDetails", id=channel_id)
    response = YouTubeChannelListResponse.from_dict(
        request.execute()
    )
    if response.pageInfo.totalResults == 0:
        return None

    return response.items[0].contentDetails.relatedPlaylists.uploads


def ensure_upload_playlists(youtube: api.Resource, data: HolocraftData):
    for channel_id in chain(data.members.values(), data.clippers):
        if channel_id not in data.upload_playlists:
            upload_playlist_id = get_upload_playlist_id(youtube, channel_id)
            if upload_playlist_id is not None:
                print(
                    f"Now tracking upload playlist {upload_playlist_id} for channel {channel_id}"
                )
                data.upload_playlists[channel_id] = upload_playlist_id
            else:
                print(f"Failed to get upload playlist for {channel_id}")


def playlist_videos(youtube: api.Resource, playlist_id: str):
    global total_quota_usage

    page_token = None
    while True:
        total_quota_usage += 1
        request = youtube.playlistItems().list(
            part="contentDetails,snippet",
            maxResults=50,
            playlistId=playlist_id,
            pageToken=page_token,
        )
        response = YouTubePlaylistListResponse.from_dict(
            request.execute()
        )

        for playlist_item in response.items:
            yield playlist_item

        if response.nextPageToken is None:
            break
        page_token = response.nextPageToken


def is_minecraft_video(playlist_item: YouTubePlaylistItemResource):
    global total_html_fetches

    # If we see minecraft in the video title we can save some time
    normalized_title = playlist_item.snippet.title.lower()
    if any(indicator in normalized_title for indicator in ["minecraft", "マイクラ"]):
        return True

    # Otherwise we try the weird strategy of finding the explicit string "Minecraft" with quotes
    # which matches the a javascript payload on the video page for the meta game info block.
    # This will probably break some day in the distant future.
    #
    # Why would YouTube add this useful metadata to the API? Don't be ridiculous.
    total_html_fetches += 1
    video_page = requests.get(
        f"https://youtube.com/watch?v={playlist_item.contentDetails.videoId}"
    )
    return re.search(r"\"simpleText\":\"Minecraft\"", video_page.text) is not None


def update_source_streams(youtube: api.Resource, data: HolocraftData):
    for member_name, member_channel_id in data.members.items():
        print("Processing member channel:", member_name)
        dirty = False
        upload_playlist_id = data.upload_playlists[member_channel_id]
        if member_channel_id not in data.seen_videos:
            data.seen_videos[member_channel_id] = set()

        for playlist_item in playlist_videos(youtube, upload_playlist_id):
            snippet = playlist_item.snippet
            content_details = playlist_item.contentDetails

            video_id = content_details.videoId
            if video_id not in data.seen_videos[member_channel_id]:
                dirty = True
                if is_minecraft_video(playlist_item):
                    print(f"{video_id}: {snippet.channelTitle} - {snippet.title}")
                    # Add this source stream to the holocraft database
                    data.craft_streams[video_id] = HolocraftStream(
                        member_channel_id, content_details.videoPublishedAt
                    )

                # Mark this video as seen so we don't process it again
                data.seen_videos[member_channel_id].add(video_id)

        # Checkpoint the data to disk after each channel
        if dirty:
            write_data(data)


def update_clips(youtube: api.Resource, data: HolocraftData):
    for clipper_channel_id in data.clippers:
        print("Processing clip channel", clipper_channel_id)
        dirty = False
        upload_playlist_id = data.upload_playlists[clipper_channel_id]
        if clipper_channel_id not in data.seen_videos:
            data.seen_videos[clipper_channel_id] = set()

        for playlist_item in playlist_videos(youtube, upload_playlist_id):
            snippet = playlist_item.snippet
            video_id = playlist_item.contentDetails.videoId
            if video_id not in data.seen_videos[clipper_channel_id]:
                dirty = True
                source_stream_ids = [
                    match[1]  # just the video ID
                    for match in re.findall(
                        r"(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)",
                        snippet.description,
                    )
                ]
                if len(source_stream_ids) == 0:
                    print(video_id, "has no source streams!")
                else:
                    print(video_id, ":", ", ".join(source_stream_ids))
                    data.craft_clips[video_id] = HolocraftClip(source_stream_ids)

                # Mark this video as seen so we don't process it again
                data.seen_videos[clipper_channel_id].add(video_id)

        # Checkpoint data to disk after each channel
        if dirty:
            write_data(data)


def load_data():
    with open(DATAFILE_PATH, "r") as holocraft_data_file:
        data = HolocraftData.from_json(holocraft_data_file.read())
        return data


def do_write_data(data: HolocraftData):
    with open(DATAFILE_PATH, "w") as holocraft_data_file:
        holocraft_data_file.write(json.dumps(data.to_dict(), indent=2))


def write_data(data: HolocraftData):
    write_time = timeit(lambda: do_write_data(data), setup="gc.enable()", number=1)
    print(f"Wrote data in {write_time} seconds:")


def main():
    api_key = sys.argv[1]
    youtube = api.build("youtube", "v3", developerKey=api_key)

    # Load existing data
    data = load_data()

    # Do update
    ensure_upload_playlists(youtube, data)
    update_source_streams(youtube, data)
    update_clips(youtube, data)

    # Write out
    write_data(data)
    print("Total quota usage:", total_quota_usage)
    print("Total html fetches", total_html_fetches)


if __name__ == "__main__":
    main()
