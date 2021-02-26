<script lang="ts">
  import Icon from "svelte-fa";
  import {
    faCalendarDay,
    faCalendarAlt,
    faCalendar,
  } from "@fortawesome/free-solid-svg-icons";

  import TimelineMark from "./TimelineMark.svelte";
  import type dayjs from "dayjs";
  import type { Granularity } from "./data/dateTree";
  import { formatGranularity } from "./data/dateTree";

  export let date: dayjs.Dayjs;
  export let granularity: Granularity;
  export let onClick: () => void = () => {};

  function getGranularityIcon(granularity: Granularity) {
    switch (granularity) {
      case "year":
        return faCalendar;
      case "month":
        return faCalendarAlt;
      case "date":
        return faCalendarDay;
      default:
        return faCalendar;
    }
  }
</script>

<TimelineMark>
  <div
    slot="mark"
    class="relative z-10 flex items-center justify-center w-12 h-12 bg-white rounded-full cursor-pointer"
    on:click={onClick}
  >
    <Icon icon={getGranularityIcon(granularity)} size="lg" />
  </div>
  <div
    slot="attachment"
    class="flex flex-row items-center justify-start w-64 h-full text-white"
  >
    <slot>
      {formatGranularity(date, granularity)}
    </slot>
  </div>
</TimelineMark>
