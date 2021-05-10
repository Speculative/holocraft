import { writable } from "svelte/store";
import { bindDispatch } from "./storeUtils";

export interface PlayerEntry {
  videoId: string;
  type: "stream" | "clip";
}

interface VideoPlayer {
  playlist: PlayerEntry[];
  nowPlaying?: string;
}

function enqueue(
  player: VideoPlayer,
  videoId: string,
  type: "stream" | "clip"
) {
  const newEntry = { videoId, type };
  if (!player.playlist.find((entry) => entry.videoId === videoId)) {
    player.playlist.push(newEntry);

    if (player.nowPlaying === undefined) {
      player.nowPlaying = videoId;
    }
  }
}

function advance(player: VideoPlayer) {
  const nowPlayingIndex =
    player.playlist.findIndex((entry) => entry.videoId === player.nowPlaying) ??
    0;

  const nextEntry = player.playlist[nowPlayingIndex + 1];
  player.nowPlaying = nextEntry?.videoId;
}

function jumpTo(player: VideoPlayer, videoId: string) {
  const entryIndex = player.playlist.findIndex(
    (entry) => entry.videoId === videoId
  );

  if (entryIndex !== undefined) {
    player.nowPlaying = videoId;
  }
}

function reorder(player: VideoPlayer, newOrder: string[]) {
  const currentEntries = Object.fromEntries(
    player.playlist.map((entry) => [entry.videoId, entry])
  );
  player.playlist = newOrder.map((id) => currentEntries[id]);
}

function createVideoPlayerStore() {
  const { subscribe, update } = writable<VideoPlayer>({
    playlist: [],
  });

  return {
    subscribe,
    enqueue: bindDispatch(update, enqueue),
    advance: bindDispatch(update, advance),
    jumpTo: bindDispatch(update, jumpTo),
    reorder: bindDispatch(update, reorder),
  };
}

export const videoPlayerStore = createVideoPlayerStore();
