<script lang="ts">
  import TimelineMark from "./TimelineMark.svelte";
  import type dayjs from "dayjs";
  import type { Granularity } from "./data/dateTree";

  export let date: dayjs.Dayjs;
  export let granularity: Granularity;
  export let onClick: () => void = () => {};

  function formatGranularity(date: dayjs.Dayjs, granularity: Granularity) {
    switch (granularity) {
      case "year":
        return date.format("YYYY");
      case "month":
        return date.format("MMMM YYYY");
      case "date":
        return date.format("MMMM D");
      default:
        return date.format("MMMM D, YYYY");
    }
  }
</script>

<TimelineMark>
  <div
    slot="mark"
    class="relative z-10 flex items-center justify-center w-12 h-12 bg-white rounded-full cursor-pointer"
    on:click={onClick}
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M12 6v6m0 0v6m0-6h6m-6 0H6"
      />
    </svg>
  </div>
  <div
    slot="attachment"
    class="flex flex-row items-center justify-start w-64 h-full text-white"
  >
    {formatGranularity(date, granularity)}
  </div>
</TimelineMark>
