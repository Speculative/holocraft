import produce from "immer";
import { writable } from "svelte/store";

export interface PlayerEntry {
  videoId: string;
  type: "stream" | "clip";
}

interface VideoPlayer {
  history: PlayerEntry[];
  nowPlaying?: PlayerEntry;
  queue: PlayerEntry[];
}

function bindDispatch<TState, TProducerArgs extends any[]>(
  update: (updater: (currentState: TState) => TState) => void,
  producer: (draftState: TState, ...args: TProducerArgs) => void
) {
  return function (...producerArgs: TProducerArgs) {
    update((currentState: TState) =>
      produce(currentState, (draftState: TState) =>
        producer(draftState, ...producerArgs)
      )
    );
  };
}

function enqueue(
  player: VideoPlayer,
  videoId: string,
  type: "stream" | "clip"
) {
  const entry = { videoId, type };
  if (!player.nowPlaying) {
    player.nowPlaying = entry;
  } else if (
    player.nowPlaying.videoId !== videoId &&
    !player.queue.find((entry) => entry.videoId === videoId)
  ) {
    player.queue.push(entry);
  }
}

function playImmediately(
  player: VideoPlayer,
  videoId: string,
  type: "stream" | "clip"
) {
  if (player.nowPlaying !== undefined) {
    player.history.push(player.nowPlaying);
  }
  player.nowPlaying = { videoId, type };
}

function advance(player: VideoPlayer) {
  const [nextEntry, ...restOfQueue] = player.queue;
  if (player.nowPlaying !== undefined) {
    player.history.push(player.nowPlaying);
  }
  player.nowPlaying = nextEntry;
  player.queue = restOfQueue;
}

function jumpTo(player: VideoPlayer, videoId: string) {
  const queueIndex = player.queue.findIndex(
    (entry) => entry.videoId === videoId
  );
  if (queueIndex !== undefined) {
    const [jumpToEntry, _] = player.queue.splice(queueIndex, 1);
    if (player.nowPlaying) {
      player.history.push(player.nowPlaying);
    }
    player.nowPlaying = jumpToEntry;
  }
}

function createVideoPlayerStore() {
  const { subscribe, update } = writable<VideoPlayer>({
    queue: [],
    history: [],
  });

  return {
    subscribe,
    enqueue: bindDispatch(update, enqueue),
    playImmediately: bindDispatch(update, playImmediately),
    advance: bindDispatch(update, advance),
    jumpTo: bindDispatch(update, jumpTo),
  };
}

export const videoPlayerStore = createVideoPlayerStore();
