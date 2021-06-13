<script lang="ts">
  import "plyr/dist/plyr.css";

  import Plyr from "plyr";
  import { afterUpdate } from "svelte";

  import type { PlayerEntry } from "./data/videoPlayerStore";
  import { videoPlayerStore } from "./data/videoPlayerStore";
  import { holocraftData } from "./data/dataStore";
  import Playlist from "./Playlist.svelte";

  let started = false;
  $: if ($videoPlayerStore.nowPlaying !== undefined && !started) {
    started = true;
  }

  let plyrHost: HTMLElement;
  let plyr: Plyr | undefined;

  afterUpdate(() => {
    if (plyrHost && !plyr) {
      plyr = new Plyr(plyrHost, {
        autoplay: true,
      });
      plyr.on("statechange", (stateChange) => {
        if (stateChange.detail.code === 0 /* Ended state */) {
          videoPlayerStore.advance();
        }
      });
    }
  });

  $: nowPlayingId = $videoPlayerStore.nowPlaying; // TS won't narrow this undefined below unless we hide the reactive store dereference?

  let plyrCurrentVideo: string | undefined = undefined;
  $: if (
    plyr &&
    nowPlayingId !== undefined &&
    nowPlayingId !== plyrCurrentVideo
  ) {
    plyrCurrentVideo = nowPlayingId;
    plyr.source = {
      type: "video",
      sources: [
        {
          src: nowPlayingId,
          provider: "youtube",
        },
      ],
    };
  }

  $: if (plyr && plyrCurrentVideo !== undefined && nowPlayingId === undefined) {
    plyr.stop();
  }

  function toSource(entry: PlayerEntry) {
    if (entry.type === "stream") {
      return {
        ...$holocraftData.streams.byId[entry.videoId],
        id: entry.videoId,
      };
    } else {
      return { ...$holocraftData.clips[entry.videoId], id: entry.videoId };
    }
  }

  $: playlistItems = $videoPlayerStore.playlist.map(toSource);
  $: console.log(playlistItems, nowPlayingId);
</script>

<div class="flex flex-col w-full h-full">
  <div class="relative aspect-16-9">
    <div class="absolute top-0 bottom-0 left-0 right-0 overflow-hidden">
      {#if started}
        <div
          bind:this={plyrHost}
          data-plyr-provider="youtube"
          data-plyr-embed-id={nowPlayingId}
        />
      {:else}
        <div
          class="flex items-center justify-center w-full h-full text-2xl font-bold text-white bg-black"
        >
          Welcome to Holocraft!
        </div>
      {/if}
    </div>
  </div>
  <div class="flex-grow overflow-hidden bg-gray-900">
    <Playlist {nowPlayingId} items={playlistItems} />
  </div>
</div>

<style>
  .aspect-16-9 {
    width: 100%;
    padding-top: 28.125%;
    padding-bottom: 28.125%;
  }
</style>
