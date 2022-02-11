from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import KW_ONLY, dataclass, field
from typing import Optional


@dataclass(kw_only=True)
class Metrics:
    souls: int = 0
    item_souls: int = 0

    def __add__(self, other: Metrics) -> Metrics:
        return Metrics(
            souls=self.souls + other.souls,
            item_souls=self.item_souls + other.item_souls,
        )


@dataclass(kw_only=True)
class State:
    metrics: Metrics = Metrics()
    bonfire: str = ""
    region: str = ""
    bonfire_to_region: dict[str, str] = field(default_factory=dict, repr=False)
    equipment: dict[str, str] = field(default_factory=dict, repr=False)
    items: Counter[str] = field(default_factory=Counter, repr=False)


@dataclass(kw_only=True, init=False)
class __Event:
    location: str = ""
    notes: str = ""


# workaround a mypy bug: https://github.com/python/mypy/issues/5374
class Event(ABC, __Event):
    @abstractmethod
    def __call__(self, state: State):
        ...


@dataclass
class Region(Event):
    location: str  # override

    def __call__(self, state: State):
        state.region = self.location


@dataclass
class BonfireSit(Event):
    location: str  # override

    def __call__(self, state: State):
        known_region = state.bonfire_to_region.get(self.location)
        if known_region is not None and known_region != state.region:
            raise RuntimeError(
                f'Bonfire "{self.location}" was previously listed as being in'
                f' region "{known_region}" but is currently indicated to be in'
                f' region "{state.region}"'
            )
        state.bonfire_to_region[self.location] = state.region
        state.bonfire = self.location


@dataclass
class BonfireAuto(BonfireSit):
    ...  # class only exists to rename the event in __str__


@dataclass(kw_only=True, init=False)
class __WarpCommon(Event):
    destination: str = ""

    def __call__(self, state: State):
        state.region = state.bonfire_to_region[self.destination]


@dataclass
class Warp(__WarpCommon):
    destination: str  # override


@dataclass(init=False)
class HomewardBone(__WarpCommon):
    def __call__(self, state: State):
        self.destination = state.bonfire
        super().__call__(state)
        state.items["Homeward Bone"] -= 1


@dataclass
class Darksign(__WarpCommon):
    def __call__(self, state: State):
        self.destination = state.bonfire
        super().__call__(state)
        state.metrics.souls = 0


@dataclass(kw_only=True)
class __EquipCommon(Event):
    slot: str
    replaces: str = ""
    expected_to_replace: Optional[str] = None

    def __call__(self, state: State):
        self.replaces = state.equipment.get(self.slot, "")
        if (
            self.expected_to_replace is not None
            and self.expected_to_replace != self.replaces
        ):
            raise RuntimeError(
                f'Expected to replace "{self.expected_to_replace}" in slot'
                f' "{self.slot}" but found different item "{self.replaces}"'
            )


@dataclass
class Equip(__EquipCommon):
    item: str
    slot: str  # override

    def __call__(self, state: State):
        super().__call__(state)
        state.equipment[self.slot] = self.item


@dataclass
class UnEquip(__EquipCommon):
    slot: str  # override

    def __call__(self, state: State):
        super().__call__(state)
        state.equipment[self.slot] = ""


@dataclass
class EquipAuto(Equip):
    ...  # class only exists to rename the event in __str__


@dataclass
class Loot(Event):
    item: str
    _ = KW_ONLY
    item_souls: int = 0
    count: int = 1

    def __call__(self, state: State):
        state.items[self.item] += self.count
        state.metrics.item_souls += self.item_souls * self.count


@dataclass
class Receive(Loot):
    ...  # class only exists to rename the event in __str__


_SOUL_ITEM_VALUES: dict[str, int] = {
    "Soul of a Lost Undead": 200,
    "Large Soul of a Lost Undead": 400,
}


@dataclass(kw_only=True)
class LootSoul(Loot):
    item_souls: int = field(default=0, init=False)  # override

    def __call__(self, state: State):
        self.item_souls = _SOUL_ITEM_VALUES[self.item] * self.count
        super().__call__(state)


@dataclass
class Buy(Event):
    item: str
    _ = KW_ONLY
    souls: int = 0
    count: int = 1

    def __call__(self, state: State):
        state.items[self.item] += self.count
        state.metrics.souls -= self.souls * self.count


@dataclass
class Activate(Event):
    target: str

    def __call__(self, state: State):
        ...


@dataclass
class Talk(Activate):
    ...  # class only exists to rename the event in __str__


@dataclass
class Kill(Event):
    target: str
    souls: int

    def __call__(self, state: State):
        state.metrics.souls += self.souls


@dataclass
class KillAuto(Kill):
    ...  # class only exists to rename the event in __str__
