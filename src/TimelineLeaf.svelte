<script lang="ts">
  import type dayjs from "dayjs";

  import type { HolocraftStream } from "./data/dataStore";
  import type { Granularity } from "./data/dateTree";
  import DateMark from "./DateMark.svelte";
  import MemberStreamMark from "./MemberStreamMark.svelte";

  export let streams: HolocraftStream[];
  export let date: dayjs.Dayjs;
  export let granularity: Granularity;

  let expanded: boolean = false;
  function toggleExpand() {
    expanded = !expanded;
  }
</script>

<section class="relative flex flex-col items-center w-16">
  <DateMark {date} {granularity} onClick={toggleExpand} />
  {#if expanded}
    {#each streams as stream}
      <MemberStreamMark member={stream.member} streamVideoId={stream.videoId} />
    {/each}
  {/if}
</section>
