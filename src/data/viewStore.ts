import { writable } from "svelte/store";
import { bindDispatch } from "./storeUtils";
import { members as orderedMembers } from "./members";

function addMemberFilters(currentMembers: string[], membersToAdd: string[]) {
  return [...new Set([...currentMembers, ...membersToAdd])].sort(
    (memberA, memberB) =>
      orderedMembers.indexOf(memberA) - orderedMembers.indexOf(memberB)
  );
}

function removeMemberFilters(
  currentMembers: string[],
  membersToRemove: string[]
) {
  const staged = new Set(currentMembers);
  membersToRemove.forEach((member) => staged.delete(member));

  return [...staged].sort(
    (memberA, memberB) =>
      orderedMembers.indexOf(memberA) - orderedMembers.indexOf(memberB)
  );
}

function createMemberFilters() {
  const { subscribe, update } = writable([] as string[]);

  return {
    subscribe,
    addMemberFilters: bindDispatch(update, addMemberFilters),
    removeMemberFilters: bindDispatch(update, removeMemberFilters),
  };
}

export const memberFilters = createMemberFilters();
export const activeCalloutStreamId = writable(null as string | null);
export const invertTimeline = writable(false);
export const hideClipless = writable(false);
