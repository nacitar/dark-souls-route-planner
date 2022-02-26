from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from itertools import chain
from typing import Optional


class Item:
    BONE = "Homeward Bone"
    DARKSIGN = "Darksign"


@dataclass(kw_only=True)
class State:
    souls: int = 0
    bank: int = 0
    bonfire: str = ""
    region: str = ""
    bonfire_to_region: dict[str, str] = field(default_factory=dict, repr=False)
    equipment: dict[str, str] = field(default_factory=dict, repr=False)
    inventory: Counter[str] = field(default_factory=Counter, repr=False)
    bank_lookup: dict[str, int] = field(default_factory=dict, repr=False)

    @property
    def bones(self):
        return self.inventory[Item.BONE]

    @bones.setter
    def bones(self, value: int):
        self.inventory[Item.BONE] = value

    def verify(self):
        overdrafts: list[str] = [
            f"{key}({value})"
            for key, value in chain(
                self.inventory.items(),
                [("souls", self.souls), ("bank", self.bank)],
            )
            if value < 0
        ]
        if overdrafts:
            raise RuntimeError("insufficent amount: " + " ".join(overdrafts))


@dataclass
class Action:
    target: str
    detail: str = field(default="", kw_only=True)
    optional: bool = field(default=False, kw_only=True)

    def __post_init__(self) -> None:
        ...  # so code doesn't need changed if this is added later

    @property
    def display(self):
        return self.target

    @property
    def name(self):
        return f"{'Optional' if self.optional else ''}{type(self).__name__}"

    def __call__(self, state: State) -> None:
        ...


@dataclass
class FallDamage(Action):
    ...


@dataclass
class Region(Action):
    detail: str = field(init=False)

    def __call__(self, state: State) -> None:
        state.region = self.target


@dataclass
class BonfireSit(Action):
    def __call__(self, state: State) -> None:
        known_region = state.bonfire_to_region.get(self.target)
        if known_region is not None and known_region != state.region:
            raise RuntimeError(
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
    replaces: str = ""
    expected_to_replace: Optional[str] = None

    def __call__(self, state: State) -> None:
        self.replaces = state.equipment.get(self.slot, "")
        if (
            self.expected_to_replace is not None
            and self.expected_to_replace != self.replaces
        ):
            raise RuntimeError(
                f'expected to replace "{self.expected_to_replace}" in slot'
                f' "{self.slot}" but found different item "{self.replaces}"'
            )


@dataclass
class Equip(__EquipCommon):
    @property
    def display(self) -> str:
        output = self.target
        if self.replaces:
            output += f" replacing {self.replaces}"
        return output

    def __call__(self, state: State) -> None:
        super().__call__(state)
        if state.inventory[self.target] <= 0:
            raise RuntimeError(
                f"Cannot equip item not in inventory: {self.target}"
            )
        state.equipment[self.slot] = self.target


@dataclass
class UnEquip(__EquipCommon):
    target: str = field(default="", init=False)

    def __call__(self, state: State) -> None:
        self.target = state.equipment.get(self.slot, "")
        super().__call__(state)
        state.equipment[self.slot] = ""


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


@dataclass(kw_only=True)
class Loot(__ItemCommon):
    bank: int = 0

    def __call__(self, state: State) -> None:
        if not self.bank:
            self.bank = state.bank_lookup.get(self.target, 0)
        else:
            stored_bank = state.bank_lookup.setdefault(self.target, self.bank)
            if stored_bank != self.bank:
                raise RuntimeError(
                    f"Previously indicated {self.target} banked"
                    f" {stored_bank} but now indicating it"
                    f" banks {self.bank}"
                )
        state.inventory[self.target] += self.count
        state.bank += self.bank * self.count


@dataclass
class Receive(Loot):
    ...


@dataclass
class UseMenu(__ItemCommon):
    def __call__(self, state: State) -> None:
        actual_count = state.inventory[self.target]
        if actual_count < self.count:
            raise RuntimeError(
                f"Cannot use {self.count} of {self.target}, only have"
                f" {actual_count}"
            )
        if self.target in (Item.BONE, Item.DARKSIGN):
            try:
                state.region = state.bonfire_to_region[state.bonfire]
            except KeyError:
                raise RuntimeError("Can't warp; bonfire region is unknown.")

        stored_bank = state.bank_lookup.get(self.target, 0)
        if stored_bank:
            delta = stored_bank * self.count
            state.souls += delta
            state.bank -= delta
        if self.target != Item.DARKSIGN:
            state.inventory[self.target] -= self.count


@dataclass
class Use(UseMenu):
    def __call__(self, state: State) -> None:
        if self.target not in state.equipment.values():
            raise RuntimeError(f"Cannot use unequipped item: {self.target}")
        super().__call__(state)
        if not state.inventory[self.target]:
            for slot, piece in state.equipment.items():
                if piece == self.target:
                    del state.equipment[slot]
                    break


@dataclass(kw_only=True)
class Kill(__ItemCommon):
    souls: int

    def __call__(self, state: State) -> None:
        state.souls += self.souls * self.count


@dataclass
class AutoKill(Kill):
    ...


@dataclass(kw_only=True)
class Buy(Kill):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.souls *= -1

    def __call__(self, state: State) -> None:
        super().__call__(state)
        state.inventory[self.target] += self.count


@dataclass
class Heal(Action):
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
class Talk(Action):
    ...
