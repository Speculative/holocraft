<script lang="ts">
  import Icon from "svelte-fa";
  import { faWindowClose, faFilm } from "@fortawesome/free-solid-svg-icons";

  import TimelineMark from "./TimelineMark.svelte";
  import Thumbnail from "./Thumbnail.svelte";
  import { holocraftData } from "./data/dataStore";
  import { videoPlayerStore } from "./data/videoPlayerStore";
  import { activeCalloutStreamId } from "./data/viewStore";

  export let member: string;
  export let streamVideoId: string;

  $: memberInfo = $holocraftData.members[member];
  $: stream = $holocraftData.streams.byId[streamVideoId];
  $: showCallout = $activeCalloutStreamId === streamVideoId;

  let showTooltip: boolean = false;

  function startHover() {
    if (!showCallout) {
      showTooltip = true;
    }
  }

  function stopHover() {
    showTooltip = false;
  }

  function toggleCallout() {
    showTooltip = false;
    activeCalloutStreamId.set(showCallout ? null : streamVideoId);
  }
</script>

<TimelineMark>
  <div
    class="box-content relative w-12 h-12 transition-all duration-100 ease-in-out bg-white border-2 rounded-full hover:border-white hover:border-4 hover:w-14 hover:h-14"
    slot="mark"
  >
    <button
      on:mouseover={startHover}
      on:mouseout={stopHover}
      on:click={toggleCallout}
      class="w-full h-full overflow-hidden rounded-full "
    >
      <img src={memberInfo.channelImageUrl} alt={memberInfo.name} />
    </button>
    {#if stream.clips.length > 0}
      <div
        class="absolute flex items-center justify-center w-5 h-5 bg-white rounded-full pointer-events-none -bottom-1 -right-1"
      >
        <Icon class="text-black" icon={faFilm} size="sm" />
      </div>
    {/if}
  </div>
  <div slot="attachment" class="flex flex-row items-center h-full">
    {#if showTooltip}
      <aside class="w-64 vertically-aligned-row">
        <div class="absolute z-0 w-2 h-2 -ml-1 transform rotate-45 bg-white" />
        <div class="relative z-20 p-2 bg-white rounded-sm">
          {memberInfo.name}
        </div>
      </aside>
    {/if}
    {#if showCallout}
      <div class="callout vertically-aligned-row">
        <div class="absolute z-0 w-2 h-2 -ml-1 transform rotate-45 bg-white" />
        <div class="relative z-10 p-4 bg-white rounded-sm">
          <a
            class:separator={stream.clips.length > 0}
            class="block p-2 mt-1 transition-all duration-200 rounded-sm hover:bg-gray-200"
            href={`https://www.youtube.com/watch?v=${stream.videoId}`}
            on:click|preventDefault={() =>
              videoPlayerStore.enqueue(stream.videoId, "stream")}
          >
            <div class="flex flex-row">
              <div class="thumbnail-box">
                <Thumbnail
                  videoId={streamVideoId}
                  title={stream.title}
                  duration={stream.duration}
                />
              </div>
              <div class="flex flex-row items-center justify-start w-2/3 pl-4">
                {stream.title}
              </div>
            </div>
          </a>
          {#if stream.clips.length > 0}
            <div class="mx-4 my-1 border-b-2 border-gray-200 rounded-full" />
          {/if}
          {#each stream.clips as clip}
            <a
              class="block p-2 transition-all duration-200 rounded-sm hover:bg-gray-200"
              href={`https://www.youtube.com/watch?v=${clip.videoId}`}
              on:click={(e) => {
                e.preventDefault();
                videoPlayerStore.enqueue(clip.videoId, "clip");
              }}
            >
              <div class="flex flex-row">
                <div class="thumbnail-box">
                  <Thumbnail
                    videoId={clip.videoId}
                    title={clip.title}
                    duration={clip.duration}
                  />
                </div>
                <div
                  class="flex flex-row items-center justify-start w-2/3 px-4 py-1"
                >
                  {clip.title}
                </div>
              </div>
            </a>
          {/each}
          <button
            class="absolute w-4 h-4 right-1 top-1"
            on:click={toggleCallout}
            ><Icon icon={faWindowClose} size="sm" /></button
          >
        </div>
      </div>
    {/if}
  </div>
</TimelineMark>

<style lang="postcss">
  .vertically-aligned-row {
    @apply flex flex-row items-center;
  }

  .callout {
    width: 48rem;
    max-width: min(50vw - 16rem, 36rem);
  }

  .thumbnail-box {
    @apply w-1/3;
    max-width: 10rem;
  }
</style>
