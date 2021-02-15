<script lang="typescript">
  export let iconSrc: string;
  export let iconName: string;

  let showTooltip: boolean = false;
  let showCallout: boolean = false;

  function startHover() {
    if (!showCallout) {
      showTooltip = true;
    }
  }

  function stopHover() {
    showTooltip = false;
  }

  function toggleCallout() {
    showTooltip = false;
    showCallout = !showCallout;
  }
</script>

<section class="flex flex-row justify-center items-center relative w-full h-32">
  <button
    on:mouseover={startHover}
    on:mouseout={stopHover}
    on:click={toggleCallout}
    class="flex justify-center items-center overflow-hidden relative z-10 rounded-full bg-white w-12 h-12 transition-all duration-100 hover:border-white hover:border-4 hover:w-14 hover:h-14"
  >
    <img src={iconSrc} alt={iconName} />
  </button>

  {#if showTooltip}
    <aside
      class="absolute self-center justify-self-center flex flex-row items-center left-20 w-64"
    >
      <div class="absolute -ml-1 z-0 transform rotate-45 w-2 h-2 bg-white" />
      <div class="relative bg-white z-10 p-2 rounded-sm">
        {iconName} did a thing
      </div>
    </aside>
  {/if}

  {#if showCallout}
    <figure
      class="absolute self-center justify-self-center flex flex-row items-center left-20 w-64"
    >
      <div class="absolute -ml-1 z-0 transform rotate-45 w-2 h-2 bg-white" />
      <div class="relative bg-white z-10 p-2 rounded-sm">
        This is where the fancy embed and stuff goes
        <br />
        And let's
        <br />
        make
        <br />
        it
        <br />
        extra
        <br />
        tall
      </div>
    </figure>
  {/if}
</section>
