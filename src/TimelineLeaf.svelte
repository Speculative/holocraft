<script lang="ts">
  import type dayjs from "dayjs";

  import type { HolocraftStream } from "./data/dataStore";
  import { holocraftData } from "./data/dataStore";
  import type { Granularity } from "./data/dateTree";
  import { formatGranularity } from "./data/dateTree";
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
  <DateMark {date} {granularity} onClick={toggleExpand}>
    <div class="flex flex-col items-start justify-center w-full h-full">
      <div>
        {formatGranularity(date, granularity)}
      </div>
      <div class="flex flex-row">
        {#each streams as stream}
          <img
            class="w-8 h-8 m-1 border-2 border-white rounded-full"
            src={$holocraftData.members[stream.member].channelImageUrl}
            alt={$holocraftData.members[stream.member].name}
          />
        {/each}
      </div>
    </div>
  </DateMark>
  {#if expanded}
    {#each streams as stream}
      <MemberStreamMark member={stream.member} streamVideoId={stream.videoId} />
    {/each}
  {/if}
</section>
