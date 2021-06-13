<script lang="ts">
  import Icon from "svelte-fa";
  import { faTrash, faSort } from "@fortawesome/free-solid-svg-icons";

  import Thumbnail from "./Thumbnail.svelte";
  import { videoPlayerStore } from "./data/videoPlayerStore";
  import type { HolocraftStream, HolocraftClip } from "./data/dataStore";

  export let source: HolocraftStream | HolocraftClip;
  export let nowPlaying: boolean;
  export let dragStart: () => void;

  let hover = false;
  function startHover() {
    hover = true;
  }
  function stopHover() {
    hover = false;
  }
  function removeSelf() {
    videoPlayerStore.remove(source.videoId);
  }
</script>

<a
  class="block w-full"
  href={`https://www.youtube.com/watch?v=${source.videoId}`}
  on:click|preventDefault={() => videoPlayerStore.jumpTo(source.videoId)}
  on:mouseover={startHover}
  on:mouseout={stopHover}
>
  <div
    class:bg-gray-900={!nowPlaying}
    class:bg-gray-500={nowPlaying}
    class="flex flex-row px-4 py-2 text-white transition-all duration-100 ease-in-out hover:bg-gray-400"
  >
    <div class="thumbnail-box">
      <Thumbnail
        videoId={source.videoId}
        title={source.title}
        duration={source.duration}
      />
    </div>
    <div
      class="relative flex flex-row items-center justify-between flex-grow px-4 py-1 text-lg text-left"
    >
      <div>
        {source.title}
      </div>
      <div
        class:opacity-100={hover}
        class="flex flex-row flex-shrink-0 pl-2 transition-opacity duration-100 ease-in-out opacity-0"
      >
        <span on:click|preventDefault={removeSelf}>
          <Icon
            class="mr-2 text-gray-100 hover:text-white"
            icon={faTrash}
            size="lg"
          />
        </span>
        <span class="reorder" on:mousedown|preventDefault={dragStart}>
          <Icon
            class="text-gray-100 hover:text-white"
            icon={faSort}
            size="lg"
          />
        </span>
      </div>
    </div>
  </div>
</a>

<style lang="postcss">
  .thumbnail-box {
    @apply flex-shrink-0;
    width: 10rem;
  }

  .reorder {
    cursor: ns-resize;
  }
</style>
