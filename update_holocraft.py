import sys
import requests
import googleapiclient.discovery as api  # type: ignore
from itertools import chain
from typing import Dict, List
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from datetime import datetime

DATAFILE_PATH = "docs/data/holocraft.json"


@dataclass
class HolocraftStream(DataClassJsonMixin):
    streamed_on: datetime
    video_id: str
    clips: List[str]


@dataclass
class HolocraftData(DataClassJsonMixin):
    # Member Name -> Channel ID
    members: Dict[str, str] = field(default_factory=dict)
    # [Clipper Channel ID]
    clippers: List[str] = field(default_factory=list)
    # Channel ID -> Upload Playlist ID
    upload_playlists: Dict[str, str] = field(default_factory=dict)
    # Channel ID -> Video ID
    seen_videos: Dict[str, str] = field(default_factory=dict)
    # Video ID -> HolocraftStream
    craft_streams: Dict[str, HolocraftStream] = field(default_factory=dict)
    # Video ID -> [Source Stream IDs]
    craft_clips: Dict[str, List[str]] = field(default_factory=dict)


def get_upload_playlist_id(youtube: api.Resource, channel_id: str):
    request = youtube.channels().list(part="contentDetails", id=channel_id)
    response = request.execute()
    if response["pageInfo"]["totalResults"] == 0:
        return None

    related_playlists = response["items"][0]["contentDetails"]["relatedPlaylists"]
    if "uploads" in related_playlists:
        return related_playlists["uploads"]
    return None


def ensure_upload_playlists(youtube: api.Resource, data: HolocraftData):
    for channel_id in chain(data.members.values(), data.clippers):
        if not channel_id in data.upload_playlists:
            upload_playlist_id = get_upload_playlist_id(youtube, channel_id)
            if not upload_playlist_id is None:
                data.upload_playlists[channel_id] = upload_playlist_id


def update_source_streams(youtube: api.Resource, data: HolocraftData):
    pass


def update_clips(youtube: api.Resource, data: HolocraftData):
    pass


def main():
    api_key = sys.argv[1]
    youtube = api.build("youtube", "v3", developerKey=api_key)

    with open(DATAFILE_PATH, "r+") as holocraft_data_file:
        # Load existing data
        data = HolocraftData.from_json(holocraft_data_file.read())

        # Do update
        ensure_upload_playlists(youtube, data)
        update_source_streams(youtube, data)
        update_clips(youtube, data)

        # Write out
        holocraft_data_file.seek(0)
        holocraft_data_file.write(data.to_json())
        holocraft_data_file.truncate()


if __name__ == "__main__":
    main()
