from typing import Dict, List, Set
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, config
from datetime import datetime
from dataclasses_json.api import LetterCase, dataclass_json
from marshmallow import fields


@dataclass
class HolocraftStream:
    """Represents a single member stream video."""

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
    """Represents a single clip video."""

    # Video IDs of source streams
    source_streams: List[str]


@dataclass
class MemberInfo:
    channel_id: str = field(default_factory=str)
    name: str = field(default_factory=str)
    channel_image_url: str = field(default_factory=str)


@dataclass
class HolocraftData(DataClassJsonMixin):
    """All Holocraft data, including metadata for running the updater."""

    # Member Name -> Channel ID
    members: Dict[str, MemberInfo] = field(default_factory=dict)
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


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ClientHolocraftStream(HolocraftStream):
    video_id: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ClientHolocraftClip(HolocraftClip):
    video_id: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ClientMemberInfo(MemberInfo):
    pass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class HolocraftClientData:
    """The data shipped with the client to render the timeline."""

    members: Dict[str, ClientMemberInfo]
    craft_streams: List[ClientHolocraftStream]
    craft_clips: List[ClientHolocraftClip]

    @classmethod
    def from_holocraft_data(cls, data: HolocraftData):
        members = {
            member_id: ClientMemberInfo(
                member_info.channel_id, member_info.name, member_info.channel_image_url
            )
            for member_id, member_info in data.members.items()
        }
        filtered_craft_clips = [
            ClientHolocraftClip(source_streams, clip_id)
            for clip_id, clip in data.craft_clips.items()
            # We only take clips which have at least 1 known holocraft source stream
            if len(
                #  And we only list those source streams which are known holocraft source streams
                source_streams := [
                    craft_stream
                    for craft_stream in clip.source_streams
                    if craft_stream in data.craft_streams
                ]
            )
            > 0
        ]
        ordered_craft_streams = sorted(
            [
                ClientHolocraftStream(
                    source_stream.member, source_stream.published_at, source_stream_id
                )
                for source_stream_id, source_stream in data.craft_streams.items()
            ],
            # Sorted by date
            key=lambda stream: stream.published_at,
        )
        return cls(members, ordered_craft_streams, filtered_craft_clips)
