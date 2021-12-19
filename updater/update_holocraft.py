import json
import re
import sys
from itertools import chain
from timeit import timeit
from typing import Any, Callable, Set, TypeVar

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
    all_stream_ids = set(data.craft_streams.keys())
    seen_stream_ids = set()
    for member_name, member_info in data.members.items():
        try:
            print("Processing member channel:", member_name)
            dirty = False
            member_channel_id = member_info.channel_id
            upload_playlist_id = data.upload_playlists[member_channel_id]
            if member_channel_id not in data.seen_videos:
                data.seen_videos[member_channel_id] = set()

            for playlist_item in playlist_videos(youtube, upload_playlist_id):
                snippet = playlist_item.snippet
                content_details = playlist_item.contentDetails

                video_id = playlist_item.id
                seen_stream_ids.add(video_id)

                if video_id not in data.seen_videos[member_channel_id]:
                    dirty = True
                    if is_minecraft_video(playlist_item):
                        print(f"{video_id}: {snippet.channelTitle} - {snippet.title}")
                        # Add this source stream to the holocraft database
                        data.craft_streams[video_id] = HolocraftStream(
                            member=member_name,
                            published_at=snippet.publishedAt,
                            title=snippet.title,
                            duration=content_details.duration,
                        )

                    # Mark this video as seen so we don't process it again
                    data.seen_videos[member_channel_id].add(video_id)

            # Checkpoint the data to disk after each channel
            if dirty:
                write_data(data)
        except Exception as e:
            print(f"Failed to process streams for {member_name}:", e)
            # This is _probably_ a transient error, so let's not delete all of the member's streams
            seen_stream_ids.update(
                streamId
                for streamId, streamDetails in data.craft_streams.items()
                if streamDetails.member == member_name
            )

    to_remove = all_stream_ids - seen_stream_ids
    print(f"Removed {len(to_remove)} missing streams")
    if len(to_remove) > 0:
        print(", ".join(to_remove))
    clean_up_streams(data, to_remove)


def update_clips(youtube: api.Resource, data: HolocraftData):
    all_clip_ids = set(data.craft_clips.keys())
    seen_clip_ids = set()
    for clipper_channel_id in data.clippers:
        try:
            print("Processing clip channel", clipper_channel_id)
            dirty = False
            num_new_clips = 0

            upload_playlist_id = data.upload_playlists[clipper_channel_id]
            if clipper_channel_id not in data.seen_videos:
                data.seen_videos[clipper_channel_id] = set()

            for playlist_item in playlist_videos(youtube, upload_playlist_id):
                snippet = playlist_item.snippet
                content_details = playlist_item.contentDetails

                video_id = playlist_item.id
                seen_clip_ids.add(video_id)

                if video_id not in data.seen_videos[clipper_channel_id]:
                    dirty = True
                    source_stream_ids = [
                        match[1]  # just the video ID
                        for match in re.findall(
                            r"(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)",
                            snippet.description,
                        )
                    ]
                    if len(source_stream_ids) > 0:
                        num_new_clips += 1
                        data.craft_clips[video_id] = HolocraftClip(
                            source_streams=source_stream_ids,
                            title=snippet.title,
                            duration=content_details.duration,
                        )

                    # Mark this video as seen so we don't process it again
                    data.seen_videos[clipper_channel_id].add(video_id)

            print(f"{num_new_clips} new clips")
            # Checkpoint data to disk after each channel
            if dirty:
                write_data(data)
        except Exception as e:
            # We'll lose all of the clips for this channel
            # since we don't save clip -> clipper mappings,
            # we don't know which clips originated with this channel
            print(f"Failed to process clips for {clipper_channel_id}:", e)

    to_remove = all_clip_ids - seen_clip_ids
    print(f"Removed {len(to_remove)} missing clips")
    if len(to_remove) > 0:
        print(", ".join(to_remove))
    clean_up_clips(data, to_remove)


def clean_up_streams(data: HolocraftData, stream_ids_to_remove: Set[str]):
    for stream_id in stream_ids_to_remove:
        del data.craft_streams[stream_id]
    for member in data.members.values():
        data.seen_videos[member.channel_id] = (
            data.seen_videos[member.channel_id] - stream_ids_to_remove
        )


def clean_up_clips(data: HolocraftData, clip_ids_to_remove: Set[str]):
    for clip_id in clip_ids_to_remove:
        del data.craft_clips[clip_id]
    for clipper in data.clippers:
        data.seen_videos[clipper] = data.seen_videos[clipper] - clip_ids_to_remove


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
