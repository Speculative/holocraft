<script lang="ts">
  import { holocraftData } from "./data-store";
  import Tailwind from "./Tailwind.svelte";

  $: numStreams = Object.keys($holocraftData.streams).length;
  $: numClips = Object.keys($holocraftData.clips).length;
</script>

<!-- Tailwind init goes before everything else -->
<Tailwind />

<main class="w-full h-full bg-gray-800">
  <h1 class="text-white">Holocraft</h1>
  <p class="font-bold italic text-white">Streams: {numStreams}</p>
  <p class="font-bold text-white">Clips: {numClips}</p>
</main>
