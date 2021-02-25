<script lang="ts">
  import type { DateTree, Granularity } from "./data/dateTree";
  import type { HolocraftStream } from "./data/dataStore";
  import DateMark from "./DateMark.svelte";
  import TimelineLeaf from "./TimelineLeaf.svelte";

  export let tree: DateTree<HolocraftStream, Granularity[]>;
  /*
  This is due to some weird type narrowing behavior of TypeScript + tuple arity.
  In code like:

  ```
  const aTree: DateTree<number, Granularity[]> = new DateTree();
  if (aTree.isBottom()) {
    aTree.children // Correct: Map<string, number>
  }

  if (aTree.isNotBottom()) {
    aTree.children // Incorrect: Map<string, number> & Map<string, DateTree<number, [Granularity]>>
                   // Should be: Map<string, DateTree<number, [Granularity, ...Granularity[]]>>
  }
  ```

  Anyway, this can be fixed by having 2 type guards and 2 aliases which are refined independently.
  It's a bit awkward (and the logic is kind of wrong since it's two ifs instead of an if/else), but
  it is still type safe in each branch.

  Not that it even matters! svelte:self doesn't actually take on the prop types of the component.
  */

  $: maybeBottom = tree;
  $: maybeNotBottom = tree;

  let expanded: boolean[] = [];
  $: if (expanded.length === 0) {
    expanded = new Array(tree.keys().length).fill(false);
  }

  function toggleExpand(index: number) {
    if (expanded !== null) {
      expanded = [
        ...expanded.slice(0, index),
        !expanded[index],
        ...expanded.slice(index + 1),
      ];
    }
  }
</script>

<section class="relative flex flex-col items-center w-16">
  {#if maybeNotBottom.isNotBottom()}
    {#each maybeNotBottom.keys() as bucket, index}
      <DateMark
        date={bucket}
        granularity={maybeNotBottom.granularity()}
        onClick={() => toggleExpand(index)}
      />
      {#if expanded[index]}
        <div class="left-16 relative">
          <svelte:self tree={maybeNotBottom.get(bucket)} />
        </div>
      {/if}
    {/each}
  {/if}
  {#if maybeBottom.isBottom()}
    {#each maybeBottom.keys() as bucket}
      <TimelineLeaf
        streams={tree.unsafeGet(bucket)}
        date={bucket}
        granularity={maybeBottom.granularity()}
      />
    {/each}
  {/if}
  <div class="absolute z-0 w-2 h-full bg-white" />
</section>
