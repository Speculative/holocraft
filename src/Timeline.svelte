<script lang="ts">
  import { holocraftData } from "./data/dataStore";
  import TimelineTree from "./TimelineTree.svelte";
</script>

<section class="relative flex flex-col items-center w-16">
  <TimelineTree tree={$holocraftData.streams.byDate} />
</section>
