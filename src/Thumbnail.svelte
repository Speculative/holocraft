<script lang="ts">
  import type { Duration } from "dayjs/plugin/duration";

  export let videoId: string;
  export let title: string;
  export let duration: Duration;

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

  function formatDuration(duration: Duration) {
    // Day.js handles durations weirdly. If a particular unit isn't specified in
    // the ISO-8601 duration that was used to create the Duration object, it
    // will be formatted as "undefined"
    // https://github.com/iamkun/dayjs/issues/1521
    const days = duration.days() !== undefined ? duration.format("DD") : "00";
    const hours = duration.hours() !== undefined ? duration.format("HH") : "00";
    const minutes =
      duration.minutes() !== undefined ? duration.format("mm") : "00";
    const seconds =
      duration.seconds() !== undefined ? duration.format("ss") : "00";

    if (duration.days() > 0) {
      return `${days}:${hours}:${minutes}:${seconds}`;
    } else if (duration.hours() > 0) {
      return `${hours}:${minutes}:${seconds}`;
    } else {
      return `${minutes}:${seconds}`;
    }
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
      <div
        class="absolute px-1 text-sm font-medium text-white bg-black bg-opacity-75 bottom-1 right-1"
      >
        {formatDuration(duration)}
      </div>
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
