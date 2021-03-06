# Using the all-caps member id instead of channel in `member` field of HolocraftStream
# Parent SHA: 7e39650601f56f4c868db9e8b0fc1ccc6b30a90f

import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

import googleapiclient.discovery as api  # type: ignore
from dataclasses_json import DataClassJsonMixin, config

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
from updater.youtube import get_channel_picture


@dataclass
class HolocraftDataBefore(DataClassJsonMixin):
    members: Dict[str, str] = field(default_factory=dict)
    clippers: List[str] = field(default_factory=list)
    upload_playlists: Dict[str, str] = field(default_factory=dict)
    seen_videos: Dict[str, Set[str]] = field(
        default_factory=dict,
        metadata=config(encoder=lambda d: {k: sorted(v) for k, v in d.items()}),
    )
    craft_streams: Dict[str, HolocraftStream] = field(default_factory=dict)
    craft_clips: Dict[str, HolocraftClip] = field(default_factory=dict)


MEMBER_NAMES = {
    "GURA": "Gura",
    "CALLIOPE": "Calliope",
    "AMELIA": "Amelia",
    "INANIS": "Ina'nis",
    "KIARA": "Kiara",
    "SORA": "Sora",
    "ROBOCO": "Roboco",
    "MIKO": "Miko",
    "SUISEI": "Suisei",
    "MEL": "Mel",
    "MATSURI": "Matsuri",
    "FUBUKI": "Fubuki",
    "AKI": "Aki",
    "HAATO": "Haato",
    "AQUA": "Aqua",
    "SHION": "Shion",
    "AYAME": "Ayame",
    "CHOCO": "Choco",
    "SUBARU": "Subaru",
    "MIO": "Mio",
    "OKAYU": "Okayu",
    "KORONE": "Korone",
    "PEKORA": "Pekora",
    "RUSHIA": "Rushia",
    "FLARE": "Flare",
    "NOEL": "Noel",
    "MARINE": "Marine",
    "KANATA": "Kanata",
    "COCO": "Coco",
    "WATAME": "Watame",
    "TOWA": "Towa",
    "LUNA": "Luna",
    "LAMY": "Lamy",
    "NENE": "Nene",
    "BOTAN": "Botan",
    "POLKA": "Polka",
    "RISU": "Risu",
    "MOONA": "Moona",
    "IOFI": "Iofi",
    "OLLIE": "Ollie",
    "ANYA": "Anya",
    "REINE": "Reine",
    "MIYABI": "Miyabi",
    "KIRA": "Kira",
    "IZURU": "Izuru",
    "ARURAN": "Aruran",
    "RIKKA": "Rikka",
    "ASTEL": "Astel",
    "TEMMA": "Temma",
    "ROBERU": "Roberu",
    "SHIEN": "Shien",
    "OGA": "Oga",
}

if __name__ == "__main__":
    api_key = sys.argv[1]
    youtube = api.build("youtube", "v3", developerKey=api_key)

    data = load_with_schema(HolocraftDataBefore.from_json)
    staged_data: Any = data.to_dict()

    # Change stream member field from channel id to member id
    channel_to_member = {
        member_channel_id: member for member, member_channel_id in data.members.items()
    }
    for stream_id, stream in data.craft_streams.items():
        member_id = channel_to_member[stream.member]
        staged_data["craft_streams"][stream_id] = HolocraftStream(
            member_id, stream.published_at
        )

    # Remove the old member id -> channel id map
    staged_data["members"] = {}

    # Upgrade member info from str (channel id) -> MemberInfo
    # And also fetch channel image URLs
    for member_id, channel_id in data.members.items():
        channel_image_url = get_channel_picture(youtube, channel_id)

        staged_data["members"][member_id] = MemberInfo(
            channel_id, MEMBER_NAMES[member_id], channel_image_url
        )

    after = HolocraftData.from_dict(staged_data)

    write_with_schema(after.to_dict)
    emit_client_data(after)
