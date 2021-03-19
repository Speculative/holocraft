<script lang="ts">
  export let videoId: string;
  export let title: string;

  let currentFrame = 0;
  let cycleInterval: number | undefined = undefined;

  function startCycle() {
    cycleInterval = setInterval(() => {
      currentFrame = (currentFrame + 1) % 4;
    }, 750);
  }

  function endCycle() {
    clearInterval(cycleInterval);
    currentFrame = 0;
  }

  // https://stackoverflow.com/a/20542029
  $: frames = [
    `https://i.ytimg.com/vi/${videoId}/0.jpg`,
    `https://i.ytimg.com/vi/${videoId}/hq1.jpg`,
    `https://i.ytimg.com/vi/${videoId}/hq2.jpg`,
    `https://i.ytimg.com/vi/${videoId}/hq3.jpg`,
  ];
  $: src = frames[currentFrame];
</script>

<div class="flex items-center justify-center w-full h-full">
  <div class="relative aspect-16-9">
    <div
      class="absolute top-0 left-0 flex items-center justify-center w-full h-full overflow-hidden"
    >
      <img
        class="self-center"
        on:mouseenter={startCycle}
        on:mouseleave={endCycle}
        {src}
        alt={title}
      />
    </div>
  </div>
</div>

<style>
  .aspect-16-9 {
    height: 0;
    width: 100%;
    padding-top: 28.125%;
    padding-bottom: 28.125%;
  }
</style>
