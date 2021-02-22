import { readable } from "svelte/store";
import dayjs from "dayjs";
import { DateTree } from "./dateTree";

interface HolocraftStream {
  videoId: string;
  member: string;
  publishedAt: dayjs.Dayjs;
  clips: HolocraftClip[];
}

interface HolocraftClip {
  videoId: string;
  sourceStreams: HolocraftStream[];
}

interface HolocraftData {
  streams: {
    /**
     * Mapping of Stream video ID -> HolocraftStream
     */
    byId: { [videoId: string]: HolocraftStream };
    /**
     * Ordered array of all streams from all members from oldest to newest
     */
    inOrder: HolocraftStream[];
    /**
     * Mapping of Member -> Ordered array of streams from oldest to newest
     */
    byMember: { [member: string]: HolocraftStream[] };
    /**
     * Time-bucketed map of Year -> Month -> Day -> Streams
     */
    byDate: DateTree<HolocraftStream, ["year", "month", "day"]>;
  };
  /**
   * Mapping of Clip video ID -> HolocraftClip
   */
  clips: { [videoId: string]: HolocraftClip };
}

/**
 * This should be kept in sync with updater/holocraft_data.py:HolocraftClientData
 */
interface HolocraftJson {
  craftStreams: {
    videoId: string;
    member: string;
    publishedAt: string;
  }[];
  craftClips: {
    videoId: string;
    sourceStreams: string[];
  }[];
}

export const holocraftData = readable<HolocraftData>(
  {
    streams: {
      byId: {},
      inOrder: [],
      byMember: {},
      byDate: new DateTree([], ["year", "month", "day"]),
    },
    clips: {},
  },
  function start(set) {
    fetch("holocraft.json")
      .then((response) => response.json())
      .then((responseJson: HolocraftJson) => {
        const startTime = performance.now();

        const inOrder = responseJson.craftStreams.map(
          ({ videoId, publishedAt, member }) => ({
            member,
            videoId,
            publishedAt: dayjs(publishedAt),
            clips: [] as HolocraftClip[],
          })
        );

        const byId = Object.fromEntries(
          inOrder.map((stream) => [stream.videoId, stream])
        );

        const clips = Object.fromEntries(
          responseJson.craftClips.map(({ videoId, sourceStreams }) => [
            videoId,
            {
              videoId,
              sourceStreams: sourceStreams.map(
                (sourceStreamId) => byId[sourceStreamId]
              ),
            },
          ])
        );

        // Associate clips to streams
        for (const clip of Object.values(clips)) {
          for (const sourceStream of clip.sourceStreams) {
            sourceStream.clips.push(clip);
          }
        }

        const byMember = inOrder.reduce(
          (accumulator, stream) => ({
            ...accumulator,
            ...(stream.member in accumulator
              ? {
                  [stream.member]: [...accumulator[stream.member], stream],
                }
              : { [stream.member]: [stream] }),
          }),
          {} as { [member: string]: HolocraftStream[] }
        );

        const byDate = new DateTree(
          inOrder.map((clip) => [clip.publishedAt, clip]),
          ["year", "month", "day"] as const
        );

        const endTime = performance.now();
        console.log(`Computed stats in ${endTime - startTime} ms`);

        const finalized = {
          streams: {
            byId,
            inOrder,
            byMember,
            byDate,
          },
          clips,
        };
        (window as any).holocraftData = finalized;
        set(finalized);
      });
  }
);
