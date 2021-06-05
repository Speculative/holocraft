<script lang="ts">
  import type { HolocraftStream } from "./data/dataStore";
  import { holocraftData } from "./data/dataStore";
  import {
    memberFilters,
    hideClipless,
    invertTimeline,
  } from "./data/viewStore";
  import TimelineTree from "./TimelineTree.svelte";

  function getStreamDate(stream: HolocraftStream) {
    return stream.publishedAt;
  }

  $: applyMemberFilter = (stream: HolocraftStream) => {
    if ($memberFilters.length > 0) {
      return $memberFilters.includes(stream.member);
    }

    return true;
  };

  $: applyCliplessFilter = (stream: HolocraftStream) => {
    if ($hideClipless) {
      return stream.clips.length > 0;
    }

    return true;
  };

  $: viewFilter = (stream: HolocraftStream) => {
    return [applyMemberFilter, applyCliplessFilter].every((predicate) =>
      predicate(stream)
    );
  };
</script>

<section class="relative flex flex-col items-center w-16">
  <TimelineTree
    tree={$holocraftData.streams.byDate
      .prune(viewFilter, getStreamDate)
      .invert($invertTimeline, getStreamDate)}
  />
</section>
