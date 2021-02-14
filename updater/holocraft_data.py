import json
from typing import Dict, List, Set, Optional
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
class HolocraftData(DataClassJsonMixin):
    """All Holocraft data, including metadata for running the updater."""

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


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class HolocraftClientData:
    """The data shipped with the client to render the timeline."""

    craft_streams: Dict[str, HolocraftStream]
    craft_clips: Dict[str, HolocraftClip]

    @classmethod
    def from_holocraft_data(cls, data: HolocraftData):
        filtered_clips = {
            clip_id: clip
            for clip_id, clip in data.craft_clips.items()
            if any(
                craft_stream in clip.source_streams
                for craft_stream in data.craft_streams
            )
        }
        return cls(data.craft_streams, filtered_clips)
