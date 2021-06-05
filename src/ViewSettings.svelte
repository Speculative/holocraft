<script lang="ts">
  import { invertTimeline, hideClipless } from "./data/viewStore";
  import Toggle from "./Toggle.svelte";
</script>

<section class="p-2">
  <Toggle
    bind:checked={$invertTimeline}
    label="Invert timeline"
    id="toggle-invert-timeline"
  />
  <Toggle
    bind:checked={$hideClipless}
    label="Hide streams with no clips"
    id="toggle-hide-clipless"
  />
</section>
