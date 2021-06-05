// https://dev.to/swyx/how-to-set-up-svelte-with-tailwind-css-4fg5

const production = !process.env.ROLLUP_WATCH;
module.exports = {
  plugins: [require("@tailwindcss/forms")],
  purge: {
    enabled: production,
    content: ["./src/**/*.svelte"],
    options: {
      // https://github.com/tailwindlabs/tailwindcss/discussions/1731
      defaultExtractor: (content) => {
        return [
          ...(content.match(/[^<>"'`\s]*[^<>"'`\s:]/g) || []),
          ...(content.match(/(?<=class:)[^=>\/\s]*/g) || []),
        ];
      },
    },
  },
  variants: {
    extend: {
      borderWidth: ["hover"],
      width: ["hover"],
      height: ["hover", "first"],
      justifyContent: ["first"],
      alignItems: ["first"],
    },
  },
};
