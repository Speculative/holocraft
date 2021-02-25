<script lang="ts">
  import { holocraftData } from "./data/dataStore";
  import Tailwind from "./Tailwind.svelte";
  import Timeline from "./Timeline.svelte";

  $: numStreams = Object.keys($holocraftData.streams.inOrder).length;
  $: numClips = Object.keys($holocraftData.clips).length;
</script>

<!-- Tailwind init goes before everything else -->
<Tailwind />

<main class="w-full h-full overflow-x-hidden overflow-y-auto bg-gray-800">
  <h1 class="text-white">Holocraft</h1>
  <Timeline />
  <p class="italic font-bold text-white">Streams: {numStreams}</p>
  <p class="font-bold text-white">Clips: {numClips}</p>
</main>
