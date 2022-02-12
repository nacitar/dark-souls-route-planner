from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import KW_ONLY, dataclass, field
from typing import Optional


@dataclass(kw_only=True)
class State:
    souls: int = 0
    bank: int = 0
    bonfire: str = ""
    region: str = ""
    bonfire_to_region: dict[str, str] = field(default_factory=dict, repr=False)
    equipment: dict[str, str] = field(default_factory=dict, repr=False)
    items: Counter[str] = field(default_factory=Counter, repr=False)


@dataclass(kw_only=True, init=False)
class __Action:
    location: str = ""
    notes: str = ""


# workaround a mypy bug: https://github.com/python/mypy/issues/5374
class Action(ABC, __Action):
    @abstractmethod
    def __call__(self, state: State) -> None:
        ...


@dataclass
class Region(Action):
    location: str  # override

    def __call__(self, state: State) -> None:
        state.region = self.location


@dataclass
class BonfireSit(Action):
    location: str  # override

    def __call__(self, state: State) -> None:
        known_region = state.bonfire_to_region.get(self.location)
        if known_region is not None and known_region != state.region:
            raise RuntimeError(
                f'bonfire "{self.location}" was previously listed as being in'
                f' region "{known_region}" but is currently indicated to be in'
                f' region "{state.region}"'
            )
        state.bonfire_to_region[self.location] = state.region
        state.bonfire = self.location


@dataclass
class BonfireAuto(BonfireSit):
    ...  # class only exists to rename the action in __str__


@dataclass(kw_only=True, init=False)
class __WarpCommon(Action):
    destination: str = ""

    def __call__(self, state: State) -> None:
        state.region = state.bonfire_to_region[self.destination]


@dataclass
class Warp(__WarpCommon):
    destination: str  # override


@dataclass(init=False)
class HomewardBone(__WarpCommon):
    def __call__(self, state: State) -> None:
        self.destination = state.bonfire
        super().__call__(state)
        state.items["Homeward Bone"] -= 1


@dataclass
class Darksign(__WarpCommon):
    def __call__(self, state: State) -> None:
        self.destination = state.bonfire
        super().__call__(state)
        state.souls = 0


@dataclass(kw_only=True)
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
    item: str
    slot: str  # override

    def __call__(self, state: State) -> None:
        super().__call__(state)
        state.equipment[self.slot] = self.item


@dataclass
class UnEquip(__EquipCommon):
    slot: str  # override

    def __call__(self, state: State) -> None:
        super().__call__(state)
        state.equipment[self.slot] = ""


@dataclass
class EquipAuto(Equip):
    ...  # class only exists to rename the action in __str__


@dataclass
class Loot(Action):
    item: str
    _ = KW_ONLY
    bank: int = 0
    count: int = 1

    def __call__(self, state: State) -> None:
        state.items[self.item] += self.count
        state.bank += self.bank * self.count


@dataclass
class Receive(Loot):
    ...  # class only exists to rename the action in __str__


_SOUL_ITEM_VALUES: dict[str, int] = {
    "Soul of a Lost Undead": 200,
    "Large Soul of a Lost Undead": 400,
}


@dataclass(kw_only=True)
class LootSoul(Loot):
    bank: int = field(default=0, init=False)  # override

    def __call__(self, state: State) -> None:
        self.bank = _SOUL_ITEM_VALUES[self.item]
        super().__call__(state)


@dataclass
class Buy(Action):
    item: str
    _ = KW_ONLY
    souls: int = 0
    count: int = 1

    def __call__(self, state: State) -> None:
        state.items[self.item] += self.count
        state.souls -= self.souls * self.count


@dataclass
class Run(Action):
    location: str  # override

    def __call__(self, state: State) -> None:
        ...


@dataclass
class Jump(Run):
    ...  # class only exists to rename the action in __str__


@dataclass
class Activate(Action):
    target: str

    def __call__(self, state: State) -> None:
        ...


@dataclass
class Talk(Activate):
    ...  # class only exists to rename the action in __str__


@dataclass
class Kill(Action):
    target: str
    souls: int

    def __call__(self, state: State) -> None:
        state.souls += self.souls


@dataclass
class KillAuto(Kill):
    ...  # class only exists to rename the action in __str__
