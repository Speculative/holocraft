<script lang="ts">
  import "plyr/dist/plyr.css";

  import Plyr from "plyr";
  import { afterUpdate } from "svelte";

  import type { PlayerEntry } from "./data/videoPlayerStore";
  import { videoPlayerStore } from "./data/videoPlayerStore";
  import { holocraftData } from "./data/dataStore";
  import Thumbnail from "./Thumbnail.svelte";

  let plyrHost: HTMLElement;
  let plyr: Plyr;

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

  $: nowPlayingEntry = $videoPlayerStore.nowPlaying; // TS won't narrow this undefined below unless we hide the reactive store dereference?
  $: nowPlaying = nowPlayingEntry ? toSource(nowPlayingEntry) : null;

  let plyrCurrentVideo: string | null = null;
  $: if (plyr && nowPlaying && nowPlaying.videoId !== plyrCurrentVideo) {
    plyrCurrentVideo = nowPlaying.videoId;
    plyr.source = {
      type: "video",
      sources: nowPlaying
        ? [
            {
              src: nowPlaying.videoId,
              provider: "youtube",
            },
          ]
        : [],
    };
  }

  function toSource(entry: PlayerEntry) {
    if (entry.type === "stream") {
      return $holocraftData.streams.byId[entry.videoId];
    } else {
      return $holocraftData.clips[entry.videoId];
    }
  }

  $: history = $videoPlayerStore.history.map(toSource);
  $: queue = $videoPlayerStore.queue.map(toSource);

  $: console.log(nowPlaying, history, queue);
</script>

<div class="flex flex-col w-full h-full">
  <div class="relative aspect-16-9">
    <div class="absolute top-0 bottom-0 left-0 right-0 overflow-hidden">
      {#if nowPlaying}
        <div
          bind:this={plyrHost}
          data-plyr-provider="youtube"
          data-plyr-embed-id={nowPlaying.videoId}
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
  <div class="flex-grow overflow-auto">
    {#each history as source}
      <div class="text-gray-500 bg-gray-900 playlist-row">
        <div class="thumbnail-box">
          <Thumbnail videoId={source.videoId} title={source.title} />
        </div>
        <div class="title-box">
          {source.title}
        </div>
      </div>
    {/each}
    {#if nowPlaying}
      <div class="text-white bg-gray-700 playlist-row">
        <div class="thumbnail-box">
          <Thumbnail videoId={nowPlaying.videoId} title={nowPlaying.title} />
        </div>
        <div class="title-box">
          {nowPlaying.title}
        </div>
      </div>
    {/if}
    {#each queue as source}
      <button
        class="block w-full"
        on:click={() => videoPlayerStore.jumpTo(source.videoId)}
      >
        <div
          class="text-white transition-all duration-150 bg-gray-900 playlist-row hover:bg-gray-700"
        >
          <div class="thumbnail-box">
            <Thumbnail videoId={source.videoId} title={source.title} />
          </div>
          <div class="title-box">
            {source.title}
          </div>
        </div>
      </button>
    {/each}
  </div>
</div>

<style lang="postcss">
  .playlist-row {
    @apply px-4 py-2 flex flex-row;
  }

  .thumbnail-box {
    @apply flex-shrink-0;
    width: 10rem;
  }

  .title-box {
    @apply flex flex-row items-center px-4 py-1 text-left text-lg;
  }

  .aspect-16-9 {
    width: 100%;
    padding-top: 28.125%;
    padding-bottom: 28.125%;
  }
</style>
