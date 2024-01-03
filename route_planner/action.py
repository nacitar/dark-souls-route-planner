from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
from itertools import chain
from typing import Generator, Optional, Protocol

# TODO:
# add ability to estimate time for a segment
# fix RTSR setup for gargoyles


class Item:
    BONE = "Homeward Bone"
    HUMANITY = "Humanity"
    TWIN_HUMANITIES = "Twin Humanities"
    DARKSIGN = "Darksign"
    TITANITE_SHARD = "Titanite Shard"
    TWINKLING_TITANITE = "Twinkling Titanite"


# TODO: consider how deepcopy affects fields like notes, which really is only
# needed during execution and the final value... not every incremental copy.
@dataclass(kw_only=True)
class State:
    souls: int = 0
    item_souls: int = 0
    humanity: int = 0
    item_humanities: int = 0
    bonfire: str = ""
    region: str = ""
    bonfire_to_region: dict[str, str] = field(default_factory=dict, repr=False)
    equipment: dict[str, str] = field(default_factory=dict, repr=False)
    inventory: Counter[str] = field(default_factory=Counter, repr=False)
    souls_lookup: dict[str, int] = field(default_factory=dict, repr=False)
    humanities_lookup: dict[str, int] = field(default_factory=dict, repr=False)
    new_errors: list[str] = field(default_factory=list, repr=False)
    last_overdrafts: set[str] = field(default_factory=set, repr=False)
    notes: list[str] = field(default_factory=list, repr=False)
    error_count: int = 0

    def remove_equipment(self, item: str) -> str:
        """returns the slot the item was removed from, or an empty string."""
        for slot, piece in self.equipment.items():
            if piece == item:
                del self.equipment[slot]
                return slot
        return ""

    def clear_equipment_slot(self, slot: str):
        if slot in self.equipment:
            del self.equipment[slot]

    @property
    def bones(self) -> int:
        return self.inventory[Item.BONE]

    @property
    def titanite_shards(self) -> int:
        return self.inventory[Item.TITANITE_SHARD]

    @property
    def twinkling_titanite(self) -> int:
        return self.inventory[Item.TWINKLING_TITANITE]

    def errors(self) -> list[str]:
        overdrafts: set[str] = set(
            [
                f"{key}({value})"
                for key, value in chain(
                    self.inventory.items(),
                    [("souls", self.souls), ("item_souls", self.item_souls)],
                )
                if value < 0
            ]
        )

        if overdrafts and self.last_overdrafts != overdrafts:
            self.new_errors.append(
                "insufficent amount: " + " ".join(overdrafts)
            )
        self.last_overdrafts = overdrafts
        errors = self.new_errors
        self.new_errors = []
        self.error_count += len(errors)
        return errors


class Step(Protocol):
    def generate_events(self, state: State) -> Generator[Event, None, None]:
        ...


@dataclass
class Action:  # is a 'Step'
    target: str
    detail: str = field(default="", kw_only=True)
    optional: bool = field(default=False, kw_only=True)
    condition: bool = field(default=True, kw_only=True)
    notes: list[str] = field(default_factory=list, kw_only=True)
    output: bool = field(default=True, init=False)

    def __post_init__(self) -> None:
        ...  # so code doesn't need changed if this is added later

    @property
    def display(self) -> str:
        return self.target

    @property
    def name(self) -> str:
        return f"{'Optional' if self.optional else ''}{type(self).__name__}"

    def apply(self, state: State) -> None:
        ...

    def generate_events(self, state: State) -> Generator[Event, None, None]:
        if self.condition:
            action = deepcopy(self)  # so actions can modify themselves
            action.apply(state)
            state.notes.extend(self.notes)
            yield Event(state=deepcopy(state), action=action)
            for error in state.errors():
                yield Event(state=deepcopy(state), action=Error(error))


@dataclass(kw_only=True)
class Event:
    state: State
    action: Action


@dataclass
class FallDamage(Action):
    ...


@dataclass
class Region(Action):
    detail: str = field(init=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.output = False  # this is just for changing the state

    def apply(self, state: State) -> None:
        state.region = self.target


@dataclass
class BonfireSit(Action):
    def apply(self, state: State) -> None:
        known_region = state.bonfire_to_region.get(self.target)
        if known_region is not None and known_region != state.region:
            state.new_errors.append(
                f'bonfire "{self.target}" was previously listed as being in'
                f' region "{known_region}" but is currently indicated to be in'
                f' region "{state.region}"'
            )
        state.bonfire_to_region[self.target] = state.region
        state.bonfire = self.target


@dataclass
class AutoBonfire(BonfireSit):
    ...


@dataclass
class __EquipCommon(Action):
    slot: str
    replaces: str = field(default="", init=False)
    expected_to_replace: Optional[str] = field(default=None, kw_only=True)

    def apply(self, state: State) -> None:
        self.replaces = state.equipment.get(self.slot, "")
        if (
            self.expected_to_replace is not None
            and self.expected_to_replace != self.replaces
        ):
            state.new_errors.append(
                f'expected to replace "{self.expected_to_replace}" in slot'
                f' "{self.slot}" but found different item "{self.replaces}"'
            )


@dataclass
class Equip(__EquipCommon):
    @property
    def display(self) -> str:
        output = self.target
        if self.replaces and self.replaces != self.target:
            output += f" replacing {self.replaces}"
        return output

    def apply(self, state: State) -> None:
        super().apply(state)
        if state.inventory[self.target] <= 0:
            state.new_errors.append(
                f"Cannot equip item not in inventory: {self.target}"
            )
        state.remove_equipment(self.target)
        state.equipment[self.slot] = self.target


@dataclass
class UnEquip(__EquipCommon):
    target: str = field(default="", init=False)

    def apply(self, state: State) -> None:
        self.target = state.equipment.get(self.slot, "")
        super().apply(state)
        state.clear_equipment_slot(self.slot)


@dataclass
class AutoEquip(Equip):
    ...


@dataclass(kw_only=True)
class __ItemCommon(Action):
    count: int = 1

    @property
    def display(self) -> str:
        output = self.target
        if self.count > 1:
            output += f" (x{self.count})"
        return output

    def apply(self, state: State) -> None:
        if not self.count:
            self.output = False


@dataclass(kw_only=True)
class Loot(__ItemCommon):
    souls: int = 0
    humanities: int = 0

    def apply(self, state: State) -> None:
        if not self.souls:
            self.souls = state.souls_lookup.get(self.target, 0)
        else:
            stored_souls = state.souls_lookup.setdefault(
                self.target, self.souls
            )
            if stored_souls != self.souls:
                state.new_errors.append(
                    f"Previously indicated {self.target} gives"
                    f" {stored_souls} souls but now indicating it"
                    f" gives {self.souls} souls."
                )
        if not self.humanities:
            self.humanities = state.humanities_lookup.get(self.target, 0)
        else:
            stored_humanities = state.humanities_lookup.setdefault(
                self.target, self.humanities
            )
            if stored_humanities != self.humanities:
                state.new_errors.append(
                    f"Previously indicated {self.target} gives"
                    f" {stored_humanities} humanities but now indicating it"
                    f" gives {self.humanities} humanities."
                )
        state.inventory[self.target] += self.count
        state.item_souls += self.souls * self.count
        state.item_humanities += self.humanities * self.count


@dataclass
class Receive(Loot):
    ...


@dataclass
class WarpTo(Action):
    def apply(self, state: State) -> None:
        try:
            state.region = state.bonfire_to_region[self.target]
        except KeyError:
            raise RuntimeError("Can't warp; bonfire region is unknown.")


@dataclass(kw_only=True)
class UseMenu(__ItemCommon):
    allow_partial: bool = False
    no_warp: bool = False

    def apply(self, state: State) -> None:
        actual_count = state.inventory[self.target]
        if actual_count < self.count:
            if self.allow_partial:
                self.count = actual_count
            # NOTE: unneeded; this error is covered by 'State' overdraft checks
            # else:
            #    state.new_errors.append(
            #        f"Cannot use {self.count} of {self.target}, only have"
            #        f" {actual_count}"
            #    )
        super().apply(state)
        if not self.no_warp and self.target in (Item.BONE, Item.DARKSIGN):
            WarpTo(state.bonfire).apply(state)
        stored_souls = state.souls_lookup.get(self.target, 0)
        if stored_souls:
            delta = stored_souls * self.count
            state.souls += delta
            state.item_souls -= delta
        stored_humanities = state.humanities_lookup.get(self.target, 0)
        if stored_humanities:
            delta = stored_humanities * self.count
            state.humanity += delta
            state.item_humanities -= delta
        if self.target == Item.DARKSIGN:
            # loses souls and humanity, but the item isn't consumed
            state.souls = 0
            state.humanity = 0
        else:
            state.inventory[self.target] -= self.count  # consume the item
        # unequip it if you used the last one
        if not state.inventory[self.target]:
            state.remove_equipment(self.target)


@dataclass
class Use(UseMenu):
    def apply(self, state: State) -> None:
        if self.target not in state.equipment.values():
            state.new_errors.append(
                f"Cannot use unequipped item: {self.target}"
            )
        super().apply(state)


@dataclass(kw_only=True)
class Kill(__ItemCommon):
    souls: int

    def apply(self, state: State) -> None:
        state.souls += self.souls * self.count


@dataclass
class AutoKill(Kill):
    ...


@dataclass(kw_only=True)
class Buy(Kill):
    always: bool = False  # if set, make sure you have count, buy as needed

    def __post_init__(self) -> None:
        super().__post_init__()
        self.souls *= -1

    def apply(self, state: State) -> None:
        if not self.always:
            self.count = max(self.count - state.inventory[self.target], 0)
            if not self.count:
                self.output = False  # no need to buy anything
        super().apply(state)
        state.inventory[self.target] += self.count


@dataclass
class UpgradeItem(Kill):
    new_item: str
    items: Counter[str] = field(default_factory=Counter, repr=False)

    @property
    def display(self) -> str:
        return f"{super().display} to {self.new_item}"

    def __post_init__(self) -> None:
        super().__post_init__()
        self.souls *= -1

    def apply(self, state: State) -> None:
        super().apply(state)
        for item, count in self.items.items():
            UseMenu(item, count=(count * self.count), no_warp=True).apply(
                state
            )
        state.inventory[self.target] -= 1
        state.inventory[self.new_item] += 1
        # replace equipped item
        slot = state.remove_equipment(self.target)
        if slot:
            state.equipment[slot] = self.new_item


@dataclass
class DowngradeItem(UpgradeItem):
    ...


@dataclass
class Heal(Action):
    ...


@dataclass
class Error(Action):
    ...


@dataclass
class RunTo(Action):
    ...


@dataclass
class WaitFor(Action):
    ...


@dataclass
class Perform(Action):
    ...


@dataclass
class Jump(Action):
    ...


@dataclass
class Activate(Action):
    ...


@dataclass
class TalkTo(Action):
    ...
