<script lang="ts">
  import Icon from "svelte-fa";
  import {
    faChevronDown,
    faChevronUp,
  } from "@fortawesome/free-solid-svg-icons";

  import { generations } from "./data/members";
  import FilterSummary from "./FilterSummary.svelte";
  import ViewSettings from "./ViewSettings.svelte";
  import FilterGeneration from "./FilterGeneration.svelte";

  let collapsed = true;
  function toggleCollapse() {
    collapsed = !collapsed;
  }
</script>

<section
  class="sticky top-0 left-0 right-0 z-50 w-full text-white bg-gray-700 h-14"
>
  {#if collapsed}
    <section class="h-10">
      <FilterSummary />
    </section>
    <button
      class="collapseButton"
      on:click={toggleCollapse}
      title="Expand settings"><Icon icon={faChevronDown} size="sm" /></button
    >
  {:else}
    <section
      class="absolute top-0 left-0 flex flex-col justify-between w-full h-screen bg-gray-700"
    >
      <ViewSettings />
      <div
        class="flex-grow p-4 overflow-x-hidden overflow-y-auto border-2 border-gray-300 border-solid"
      >
        <section class="flex-shrink-0 w-full masonry">
          {#each Object.entries(generations) as [generation, members]}
            <FilterGeneration {generation} {members} />
          {/each}
        </section>
      </div>
      <button
        class="collapseButton"
        on:click={toggleCollapse}
        title="Collapse settings"><Icon icon={faChevronUp} size="sm" /></button
      >
    </section>
  {/if}
</section>

<style lang="postcss">
  .collapseButton {
    @apply flex flex-row justify-center items-center w-full outline-none bg-gray-600 h-6 flex-shrink-0;
  }

  .masonry {
    column-count: auto;
    column-width: 12rem;
  }
</style>
