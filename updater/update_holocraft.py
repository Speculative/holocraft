import json
import re
import sys
from itertools import chain
from timeit import timeit
from typing import Any, Callable, TypeVar

import googleapiclient.discovery as api  # type: ignore

from updater.holocraft_data import (
    HolocraftClientData,
    HolocraftClip,
    HolocraftData,
    HolocraftStream,
)
from updater.youtube import (
    get_html_fetches,
    get_quota_usage,
    get_upload_playlist_id,
    is_minecraft_video,
    playlist_videos,
)

# Where all sync metadata is stored
DATAFILE_PATH = "updater/holocraft_all.json"
# Where to emit the data file for rendering on the client
CLIENT_DATA_PATH = "docs/holocraft.json"


def ensure_upload_playlists(youtube: api.Resource, data: HolocraftData):
    for channel_id in chain(
        map(lambda member_info: member_info.channel_id, data.members.values()),
        data.clippers,
    ):
        if channel_id not in data.upload_playlists:
            upload_playlist_id = get_upload_playlist_id(youtube, channel_id)
            if upload_playlist_id is not None:
                print(
                    f"Now tracking upload playlist {upload_playlist_id} for channel {channel_id}"
                )
                data.upload_playlists[channel_id] = upload_playlist_id
            else:
                print(f"Failed to get upload playlist for {channel_id}")


def update_source_streams(youtube: api.Resource, data: HolocraftData):
    for member_name, member_info in data.members.items():
        print("Processing member channel:", member_name)
        dirty = False
        member_channel_id = member_info.channel_id
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
                        member=member_name,
                        published_at=content_details.videoPublishedAt,
                        title=snippet.title,
                        thumbnail_url=snippet.thumbnails["default"].url,
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
                    data.craft_clips[video_id] = HolocraftClip(
                        source_streams=source_stream_ids,
                        title=snippet.title,
                        thumbnail_url=snippet.thumbnails["default"].url,
                    )

                # Mark this video as seen so we don't process it again
                data.seen_videos[clipper_channel_id].add(video_id)

        # Checkpoint data to disk after each channel
        if dirty:
            write_data(data)


TSchemaAll = TypeVar("TSchemaAll")


def load_with_schema(deserialize: Callable[[str], TSchemaAll]) -> TSchemaAll:
    with open(DATAFILE_PATH, "r") as holocraft_data_file:
        return deserialize(holocraft_data_file.read())


def load_data():
    return load_with_schema(HolocraftData.from_json)


def write_with_schema(get_serializable_data: Callable[[], Any]):
    with open(DATAFILE_PATH, "w") as holocraft_data_file:
        holocraft_data_file.write(json.dumps(get_serializable_data(), indent=2))


def write_data(data: HolocraftData):
    write_time = timeit(
        lambda: write_with_schema(data.to_dict), setup="gc.enable()", number=1
    )
    print(f"Wrote sync metadata in {write_time} seconds")


def do_emit_client_data(data: HolocraftData):
    client_data = HolocraftClientData.from_holocraft_data(data)
    with open(CLIENT_DATA_PATH, "w") as holocraft_client_data_file:
        holocraft_client_data_file.write(json.dumps(client_data.to_dict(), indent=2))


def emit_client_data(data: HolocraftData):
    write_time = timeit(
        lambda: do_emit_client_data(data), setup="gc.enable()", number=1
    )
    print(f"Wrote client data in {write_time} seconds")


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
    emit_client_data(data)
    print("Total quota usage:", get_quota_usage())
    print("Total html fetches", get_html_fetches())


if __name__ == "__main__":
    main()
