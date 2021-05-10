import produce from "immer";

export function bindDispatch<TState, TProducerArgs extends any[]>(
  update: (updater: (currentState: TState) => TState) => void,
  producer: (draftState: TState, ...args: TProducerArgs) => void
) {
  return function (...producerArgs: TProducerArgs) {
    update((currentState: TState) =>
      produce(currentState, (draftState: TState) =>
        producer(draftState, ...producerArgs)
      )
    );
  };
}
