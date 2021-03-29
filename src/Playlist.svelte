<script lang="ts">
  import { dndzone, SHADOW_ITEM_MARKER_PROPERTY_NAME } from "svelte-dnd-action";
  import type { DndEvent as DndEventInfo, Item } from "svelte-dnd-action";
  import { flip } from "svelte/animate";

  import type { HolocraftStream, HolocraftClip } from "./data/dataStore";
  import { videoPlayerStore } from "./data/videoPlayerStore";
  import PlaylistRow from "./PlaylistRow.svelte";

  type PlaylistItem = Item & (HolocraftStream | HolocraftClip);

  export let nowPlayingId: string | undefined;
  export let items: PlaylistItem[];

  interface DnDEvent {
    detail: DndEventInfo;
  }

  const flipDurationMs = 200;
  let dragDisabled = true;

  function handleDragStart() {
    dragDisabled = false;
  }
  function handleConsider(e: DnDEvent) {
    items = e.detail.items as PlaylistItem[];
  }
  async function finalizeOrder(e: DnDEvent) {
    items = e.detail.items as PlaylistItem[];
    dragDisabled = true;
    videoPlayerStore.reorder(e.detail.items.map((item) => item.id));
  }

  function transformDraggedElement(element: HTMLElement | undefined) {
    if (element !== undefined) {
      element.style.opacity = "0";
      element.style.transition = "none";
    }
  }
</script>

<div
  class="h-full overflow-x-hidden overflow-y-auto"
  use:dndzone={{
    items,
    flipDurationMs,
    dragDisabled,
    transformDraggedElement,
  }}
  on:consider={handleConsider}
  on:finalize={finalizeOrder}
>
  {#each items as item (item.id)}
    <div class="relative" animate:flip={{ duration: flipDurationMs }}>
      <PlaylistRow
        source={item}
        nowPlaying={item.videoId === nowPlayingId}
        dragStart={handleDragStart}
      />
      {#if item[SHADOW_ITEM_MARKER_PROPERTY_NAME]}
        <div
          class="absolute top-0 bottom-0 left-0 right-0 visible transition-opacity duration-200 opacity-30"
        >
          <PlaylistRow
            source={item}
            nowPlaying={item.videoId === nowPlayingId}
            dragStart={handleDragStart}
          />
        </div>
      {/if}
    </div>
  {/each}
</div>
