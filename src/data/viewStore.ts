import { writable } from "svelte/store";
import { bindDispatch } from "./storeUtils";

interface ViewState {
  activeCalloutStreamId: string | null;
}

function setActiveCalloutStream(viewState: ViewState, streamId: string | null) {
  viewState.activeCalloutStreamId = streamId;
}

function createViewStore() {
  const { subscribe, update } = writable<ViewState>({
    activeCalloutStreamId: null,
  });

  return {
    subscribe,
    setActiveCalloutStream: bindDispatch(update, setActiveCalloutStream),
  };
}

export const viewStore = createViewStore();
