declare namespace svelte.JSX {
  interface DOMAttributes<T extends EventTarget> {
    // This shouldn't be any, but also I shouldn't have to write my own declaration for this!
    onconsider?: (event: any) => any;
    onfinalize?: (event: any) => any;
  }
}
