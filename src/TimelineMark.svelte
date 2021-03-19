<section class="relative flex flex-row w-full h-24">
  <div
    class="relative z-10 flex items-center justify-center w-full h-full flex-column"
  >
    <slot name="mark" />
  </div>
  <div class="absolute h-full left-20">
    <slot name="attachment" />
  </div>
</section>
