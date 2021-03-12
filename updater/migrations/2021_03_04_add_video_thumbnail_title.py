# Add thumbnail URL and video title of streams and clips
# Parent SHA: b7a1cdc59a200562af57b11d857ae62eb2e2ec9e

import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Set

import googleapiclient.discovery as api  # type: ignore
from dataclasses_json import DataClassJsonMixin, config
from marshmallow import fields

from updater.holocraft_data import (
    HolocraftClip,
    HolocraftData,
    HolocraftStream,
    MemberInfo,
)
from updater.update_holocraft import (
    emit_client_data,
    load_with_schema,
    write_with_schema,
)
from updater.youtube import playlist_videos


@dataclass
class HolocraftStreamBefore:
    member: str
    published_at: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )


@dataclass
class HolocraftClipBefore:
    source_streams: List[str]


@dataclass
class HolocraftDataBefore(DataClassJsonMixin):
    members: Dict[str, MemberInfo] = field(default_factory=dict)
    clippers: List[str] = field(default_factory=list)
    upload_playlists: Dict[str, str] = field(default_factory=dict)
    seen_videos: Dict[str, Set[str]] = field(
        default_factory=dict,
        metadata=config(encoder=lambda d: {k: sorted(v) for k, v in d.items()}),
    )
    craft_streams: Dict[str, HolocraftStreamBefore] = field(default_factory=dict)
    craft_clips: Dict[str, HolocraftClipBefore] = field(default_factory=dict)


if __name__ == "__main__":
    api_key = sys.argv[1]
    youtube = api.build("youtube", "v3", developerKey=api_key)

    data = load_with_schema(HolocraftDataBefore.from_json)
    staged_data: Any = data.to_dict()

    all_stream_ids = set(video_id for video_id in data.craft_streams)
    updated_stream_ids = set()
    for member_name, member_info in data.members.items():
        upload_playlist_id = data.upload_playlists[member_info.channel_id]
        for playlist_item in playlist_videos(youtube, upload_playlist_id):
            video_id = playlist_item.contentDetails.videoId
            if video_id in data.craft_streams:
                staged_data["craft_streams"][video_id] = asdict(
                    HolocraftStream(
                        member=member_name,
                        published_at=playlist_item.contentDetails.videoPublishedAt,
                        title=playlist_item.snippet.title,
                        thumbnail_url=playlist_item.snippet.thumbnails["default"].url,
                    )
                )
                updated_stream_ids.add(video_id)
    print(f"Updated {len(updated_stream_ids)} of {len(all_stream_ids)} streams")
    removed_stream_ids = all_stream_ids - updated_stream_ids
    print(
        f"Didn't update {len(removed_stream_ids)} streams: {', '.join(removed_stream_ids)}"
    )
    for removed_stream_id in removed_stream_ids:
        del staged_data["craft_streams"][removed_stream_id]
    for member in data.members.values():
        staged_data["seen_videos"][member.channel_id] = (
            data.seen_videos[member.channel_id] - removed_stream_ids
        )

    all_clip_ids = set(video_id for video_id in data.craft_clips)
    updated_clip_ids = set()
    for clipper_channel_id in data.clippers:
        upload_playlist_id = data.upload_playlists[clipper_channel_id]
        for playlist_item in playlist_videos(youtube, upload_playlist_id):
            video_id = playlist_item.contentDetails.videoId
            if video_id in data.craft_clips:
                staged_data["craft_clips"][video_id] = asdict(
                    HolocraftClip(
                        source_streams=data.craft_clips[video_id].source_streams,
                        title=playlist_item.snippet.title,
                        thumbnail_url=playlist_item.snippet.thumbnails["default"].url,
                    )
                )
                updated_clip_ids.add(video_id)
    print(f"Updated {len(updated_clip_ids)} of {len(all_clip_ids)} clips")
    removed_clip_ids = all_clip_ids - updated_clip_ids
    print(f"Didn't update {len(removed_clip_ids)} clips: {', '.join(removed_clip_ids)}")
    for removed_clip_id in removed_clip_ids:
        del staged_data["craft_clips"][removed_clip_id]
    for clipper_channel_id in data.clippers:
        staged_data["seen_videos"][clipper_channel_id] = (
            data.seen_videos[clipper_channel_id] - removed_clip_ids
        )

    after = HolocraftData.from_dict(staged_data)

    write_with_schema(after.to_dict)
    emit_client_data(after)
