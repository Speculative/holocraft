<script lang="ts">
  import TimelineMark from "./TimelineMark.svelte";
</script>

<section class="flex flex-col relative items-center w-16">
  <div
    class="flex justify-center items-center relative z-10 mb-12 rounded-full bg-white w-12 h-12"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M12 6v6m0 0v6m0-6h6m-6 0H6"
      />
    </svg>
  </div>
  <TimelineMark
    iconSrc="https://yt3.ggpht.com/ytc/AAUvwnjXQ3Gt3t3SdUMZHBhhEb_c1jqThHfDaVNJF_LJ=s176-c-k-c0x00ffffff-no-rj-mo"
    iconName="Okayu"
  />
  <TimelineMark
    iconSrc="https://yt3.ggpht.com/ytc/AAUvwnimjdERaJDGopfH8UaB0r9tr_p8uyuEWWyYVkAd5Q=s176-c-k-c0x00ffffff-no-rj-mo"
    iconName="Korone"
  />
  <div class="absolute z-0 h-full w-1 bg-white" />
</section>
