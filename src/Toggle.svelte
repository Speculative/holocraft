<script lang="ts">
  // https://codepen.io/lhermann/pen/EBGZRZ
  export let checked: boolean;
  export let label: string;
  export let id: string;
</script>

<label for={id} class="flex items-center my-2 cursor-pointer">
  <div class="relative">
    <input type="checkbox" {id} class="sr-only" bind:checked />
    <div
      class:bg-green-400={checked}
      class:bg-gray-500={!checked}
      class="block h-8 transition rounded-full w-14"
    />
    <div
      class="absolute w-6 h-6 transition bg-white rounded-full dot left-1 top-1"
    />
  </div>
  <div class="ml-3 font-medium text-white">{label}</div>
</label>

<style lang="postcss">
  input:checked ~ .dot {
    transform: translateX(100%);
  }
</style>
