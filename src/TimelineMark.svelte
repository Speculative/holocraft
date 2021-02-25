<section class="relative flex flex-row w-full h-24">
  <div
    class="flex-column relative z-10 flex items-center justify-center w-full h-full"
  >
    <slot name="mark" />
  </div>
  <div class="left-20 absolute h-full">
    <slot name="attachment" />
  </div>
</section>
