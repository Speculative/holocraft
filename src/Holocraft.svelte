<script lang="ts">
  import { holocraftData } from "./data/dataStore";
  import Tailwind from "./Tailwind.svelte";
  import Timeline from "./Timeline.svelte";
  import VideoPlayer from "./VideoPlayer.svelte";

  $: numStreams = Object.keys($holocraftData.streams.inOrder).length;
  $: numClips = Object.keys($holocraftData.clips).length;
</script>

<!-- Tailwind init goes before everything else -->
<Tailwind />

<main class="flex flex-row w-full h-full overflow-hidden bg-gray-800">
  <div class="w-6/12 h-full overflow-auto">
    <h1 class="text-white">Holocraft</h1>
    <Timeline />
    <p class="font-bold text-white">Streams: {numStreams}</p>
    <p class="font-bold text-white">Clips: {numClips}</p>
  </div>
  <div class="w-6/12 h-full">
    <VideoPlayer />
  </div>
</main>
