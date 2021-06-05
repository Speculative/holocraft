<script lang="ts">
  import { holocraftData } from "./data/dataStore";
  import { memberFilters } from "./data/viewStore";

  export let generation: string;
  export let members: string[];

  let highlightGeneration = false;
  function startGenerationHover() {
    highlightGeneration = true;
  }
  function endGenerationHover() {
    highlightGeneration = false;
  }

  $: membersChecked = Object.fromEntries(
    members.map((member) => [member, $memberFilters.includes(member)])
  );
  $: generationChecked = members.every((member) => membersChecked[member]);
  function toggleGeneration() {
    if (generationChecked) {
      memberFilters.removeMemberFilters(members);
    } else {
      memberFilters.addMemberFilters(members);
    }
  }

  function checkMember(e: Event, member: string) {
    if ((e.target as HTMLInputElement).checked) {
      memberFilters.addMemberFilters([member]);
    } else {
      memberFilters.removeMemberFilters([member]);
    }
  }
</script>

<section
  class="mb-4 rounded masonryBrick"
  class:bg-gray-500={highlightGeneration}
>
  <h1
    class="flex flex-row items-center text-lg font-bold underline"
    on:mouseenter={startGenerationHover}
    on:mouseleave={endGenerationHover}
  >
    <label for={generation} class="flex-grow py-2 cursor-pointer">
      <input
        type="checkbox"
        class="mx-2 rounded cursor-pointer"
        id={generation}
        checked={generationChecked}
        on:change={toggleGeneration}
      />
      {generation}</label
    >
  </h1>
  <ul class="list-none">
    {#each members as member}
      <li class="flex flex-row items-center rounded hover:bg-gray-500">
        <label
          for={member}
          class="flex flex-row items-center flex-grow cursor-pointer"
        >
          <input
            type="checkbox"
            class="mx-2 rounded cursor-pointer"
            id={member}
            checked={membersChecked[member]}
            on:change={(e) => checkMember(e, member)}
          />
          <img
            class="w-8 h-8 my-1 mr-2 overflow-hidden border-2 border-white rounded-full"
            src={$holocraftData.members[member].channelImageUrl}
            alt={$holocraftData.members[member].name}
          />{$holocraftData.members[member].name}</label
        >
      </li>
    {/each}
  </ul>
</section>

<style lang="postcss">
  .masonryBrick {
    break-inside: avoid;
  }
</style>
