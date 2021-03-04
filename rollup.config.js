import svelte from "rollup-plugin-svelte";
import commonjs from "@rollup/plugin-commonjs";
import resolve from "@rollup/plugin-node-resolve";
import livereload from "rollup-plugin-livereload";
import { terser } from "rollup-plugin-terser";
import typescript from "@rollup/plugin-typescript";
import postcss from "rollup-plugin-postcss";
import replace from "@rollup/plugin-replace";
import sveltePreprocess from "svelte-preprocess";

const production = !process.env.ROLLUP_WATCH;

function serve() {
  let server;

  function toExit() {
    if (server) server.kill(0);
  }

  return {
    writeBundle() {
      if (server) return;
      server = require("child_process").spawn(
        "npm",
        ["run", "start", "--", "--dev"],
        {
          stdio: ["ignore", "inherit", "inherit"],
          shell: true,
        }
      );

      process.on("SIGTERM", toExit);
      process.on("exit", toExit);
    },
  };
}

export default {
  input: "src/holocraft.ts",
  output: {
    sourcemap: !production,
    format: "iife",
    name: "app",
    file: "docs/build/holocraft.js",
    inlineDynamicImports: true,
  },
  plugins: [
    postcss({
      extract: "holocraft.css",
      sourceMap: production,
      minimize: production,
    }),
    svelte({
      emitCss: true,
      compilerOptions: {
        // enable run-time checks when not in production
        dev: !production,
        css: false,
      },
      preprocess: sveltePreprocess(),
    }),

    // If you have external dependencies installed from
    // npm, you'll most likely need these plugins. In
    // some cases you'll need additional configuration -
    // consult the documentation for details:
    // https://github.com/rollup/plugins/tree/master/packages/commonjs
    resolve({
      browser: true,
      dedupe: ["svelte"],
    }),
    commonjs(),
    replace({
      preventAssignment: true,
      // https://github.com/rollup/rollup/issues/487
      // https://github.com/rollup/rollup/issues/2881
      "process.env.NODE_ENV": production
        ? JSON.stringify("production")
        : JSON.stringify("development"),
    }),
    typescript({
      noEmitOnError: production,
      sourceMap: !production,
      inlineSources: !production,
    }),

    // In dev mode, call `npm run start` once
    // the bundle has been generated
    !production && serve(),

    // Watch the `docs` directory and refresh the
    // browser on changes when not in production
    !production && livereload("docs"),

    // If we're building for production (npm run build
    // instead of npm run dev), minify
    production && terser(),
  ],
  watch: {
    clearScreen: false,
  },
};
