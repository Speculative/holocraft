import { readable } from "svelte/store";
import dayjs from "dayjs";

interface HolocraftStream {
  videoId: string;
  member: string;
  publishedAt: dayjs.Dayjs;
  clipIds: string[];
}

interface HolocraftClip {
  videoId: string;
  sourceStreamIds: string[];
}

interface HolocraftData {
  members: { [member: string]: string };
  streams: { [videoId: string]: HolocraftStream };
  clips: { [videoId: string]: HolocraftClip };
}

/**
 * This should be kept in sync with updater/holocraft_data.py:HolocraftClientData
 */
interface HolocraftJson {
  members: { [member: string]: string };
  craftStreams: {
    [videoId: string]: {
      member: string;
      publishedAt: string;
    };
  };
  craftClips: {
    [videoId: string]: {
      sourceStreams: string[];
    };
  };
}

export const holocraftData = readable<HolocraftData>(
  {
    members: {},
    streams: {},
    clips: {},
  },
  function start(set) {
    fetch("holocraft.json")
      .then((response) => response.json())
      .then((responseJson: HolocraftJson) => {
        const baseStreams = Object.fromEntries(
          Object.entries(responseJson.craftStreams).map(
            ([videoId, craftStream]) => [
              videoId,
              {
                ...craftStream,
                videoId,
                clipIds: [] as string[],
                publishedAt: dayjs(craftStream.publishedAt),
              },
            ]
          )
        );

        const baseClips = Object.fromEntries(
          Object.entries(responseJson.craftClips).map(
            ([videoId, craftClip]) => [
              videoId,
              {
                videoId,
                sourceStreamIds: craftClip.sourceStreams,
              },
            ]
          )
        );

        for (let clip of Object.values(baseClips)) {
          for (let sourceStreamId in clip.sourceStreamIds) {
            if (sourceStreamId in baseStreams) {
              baseStreams[sourceStreamId].clipIds.push(clip.videoId);
            }
          }
        }

        set({
          members: responseJson.members,
          streams: baseStreams,
          clips: baseClips,
        });
      });
  }
);

(window as any).holocraftData = holocraftData;
