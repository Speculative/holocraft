<script lang="ts">
  import "plyr/dist/plyr.css";

  import Plyr from "plyr";
  import { afterUpdate } from "svelte";

  import { videoPlayerStore } from "./data/videoPlayerStore";

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

  $: console.log("Current:", $videoPlayerStore.currentVideoId);
  $: console.log("Queue:", $videoPlayerStore.queue);
  $: videoId = $videoPlayerStore.currentVideoId;
  $: if (plyr) {
    console.log("Setting plyr src", videoId);
    plyr.source = {
      type: "video",
      sources: videoId
        ? [
            {
              src: videoId,
              provider: "youtube",
            },
          ]
        : [],
    };
  }
</script>

<div class="flex flex-col w-full h-full">
  {#if videoId}
    <div
      bind:this={plyrHost}
      data-plyr-provider="youtube"
      data-plyr-embed-id={videoId}
    />
  {/if}
  <span class="text-white">
    {$videoPlayerStore.history.join(", ")}
  </span>
  <br />
  <span class="font-bold text-white">
    {$videoPlayerStore.currentVideoId ?? "Nothing playing yet"}
  </span>
  <br />
  <span class="text-white">
    {$videoPlayerStore.queue.join(", ")}
  </span>
  <button
    class="p-2 bg-white {$videoPlayerStore.queue.length === 0
      ? 'text-gray-700 bg-gray-400 cursor-default'
      : 'text-black'}"
    disabled={$videoPlayerStore.queue.length === 0}
    on:click={videoPlayerStore.advance}
  >
    Advance queue
  </button>
</div>
