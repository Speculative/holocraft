<script lang="ts">
  import Icon from "svelte-fa";
  import {
    faSortNumericUpAlt,
    faSortNumericDownAlt,
    faVideo,
    faVideoSlash,
  } from "@fortawesome/free-solid-svg-icons";

  import { holocraftData } from "./data/dataStore";
  import {
    memberFilters,
    invertTimeline,
    hideClipless,
  } from "./data/viewStore";

  function toggleInvertTimeline() {
    invertTimeline.set(!$invertTimeline);
  }

  function toggleHideClipless() {
    hideClipless.set(!$hideClipless);
  }
</script>

<section class="flex flex-row items-center justify-between w-full h-full px-2">
  <section>
    {#if $memberFilters.length > 0}
      <section class="flex flex-row">
        {#each $memberFilters as member}
          <img
            class="w-8 h-8 my-1 mr-2 overflow-hidden border-2 border-white rounded-full"
            src={$holocraftData.members[member].channelImageUrl}
            alt={$holocraftData.members[member].name}
            title={$holocraftData.members[member].name}
          />
        {/each}
      </section>
    {:else}
      Showing everybody
    {/if}
  </section>
  <section class="flex flex-row">
    <span
      class="cursor-pointer"
      title={$hideClipless
        ? "Hiding streams with no clips"
        : "Showing all streams"}
      on:click={toggleHideClipless}
    >
      <Icon
        icon={$hideClipless ? faVideoSlash : faVideo}
        size="lg"
        class="mx-2"
      />
    </span>

    <span
      class="cursor-pointer"
      title={$invertTimeline ? "Newest on top" : "Newest on bottom"}
      on:click={toggleInvertTimeline}
    >
      <Icon
        icon={$invertTimeline ? faSortNumericUpAlt : faSortNumericDownAlt}
        size="lg"
        class="mx-2"
      />
    </span>
  </section>
</section>
