import produce from "immer";
import { writable } from "svelte/store";

interface VideoPlayer {
  history: string[];
  currentVideoId?: string;
  queue: string[];
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

function enqueue(player: VideoPlayer, videoId: string) {
  if (player.currentVideoId === undefined) {
    player.currentVideoId = videoId;
  } else {
    player.queue.push(videoId);
  }
}

function playImmediately(player: VideoPlayer, videoId: string) {
  if (player.currentVideoId !== undefined) {
    player.history.push(player.currentVideoId);
  }
  player.currentVideoId = videoId;
}

function advance(player: VideoPlayer) {
  const [nextVideo, ...restOfQueue] = player.queue;
  if (player.currentVideoId !== undefined) {
    player.history.push(player.currentVideoId);
  }
  player.currentVideoId = nextVideo;
  player.queue = restOfQueue;
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
  };
}

export const videoPlayerStore = createVideoPlayerStore();
