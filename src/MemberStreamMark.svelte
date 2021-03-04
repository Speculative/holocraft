<script lang="ts">
  import Icon from "svelte-fa";
  import { faWindowClose } from "@fortawesome/free-solid-svg-icons";

  import TimelineMark from "./TimelineMark.svelte";
  import { holocraftData } from "./data/dataStore";
  import { videoPlayerStore } from "./data/videoPlayerStore";

  export let member: string;
  export let streamVideoId: string;

  $: memberInfo = $holocraftData.members[member];

  let showTooltip: boolean = false;
  let showCallout: boolean = false;

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
    showCallout = !showCallout;
  }
</script>

<TimelineMark>
  <button
    slot="mark"
    on:mouseover={startHover}
    on:mouseout={stopHover}
    on:click={toggleCallout}
    class="hover:border-white hover:border-4 hover:w-14 hover:h-14 box-content w-12 h-12 overflow-hidden transition-all duration-100 ease-in-out bg-white border-2 rounded-full"
  >
    <img
      class="w-full h-full"
      src={memberInfo.channelImageUrl}
      alt={memberInfo.name}
    />
  </button>
  <div slot="attachment" class="flex flex-row items-center h-full">
    {#if showTooltip}
      <aside class="vertically-aligned-row w-64">
        <div class="absolute z-0 w-2 h-2 -ml-1 transform rotate-45 bg-white" />
        <div class="above-rail p-2 bg-white rounded-sm">
          {memberInfo.name} did a thing
        </div>
      </aside>
    {/if}
    {#if showCallout}
      <figure class="vertically-aligned-row w-64">
        <div class="absolute z-0 w-2 h-2 -ml-1 transform rotate-45 bg-white" />
        <div class="above-rail relative p-4 bg-white rounded-sm">
          Sorry there's no fancy embed and related clips yet.<br />
          <button
            class="underline"
            on:click={() => videoPlayerStore.enqueue(streamVideoId)}
            >Enqueue this stream</button
          >
          <button
            class="right-1 top-1 absolute w-4 h-4"
            on:click={toggleCallout}
            ><Icon icon={faWindowClose} size="sm" /></button
          >
        </div>
      </figure>
    {/if}
  </div>
</TimelineMark>

<style lang="postcss">
  .above-rail {
    @apply relative z-10;
  }

  .vertically-aligned-row {
    @apply flex flex-row items-center;
  }
</style>
