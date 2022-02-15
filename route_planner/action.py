from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass, field
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


@dataclass
class __Action:
    target: str
    detail: str = field(default="", kw_only=True)

    def __post_init__(self) -> None:
        ...  # so code doesn't need changed if this is added later

    @property
    def display(self):
        return self.target

    @property
    def name(self):
        return type(self).__name__


# workaround a mypy bug: https://github.com/python/mypy/issues/5374
class Action(ABC, __Action):
    @abstractmethod
    def __call__(self, state: State) -> None:
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
    ...  # class only exists to rename the action in __str__


@dataclass
class __WarpCommon(Action):
    def __call__(self, state: State) -> None:
        try:
            state.region = state.bonfire_to_region[self.target]
        except KeyError:
            raise RuntimeError("Attempting to warp but bonfire is unknown.")


@dataclass
class Warp(__WarpCommon):
    ...


@dataclass
class Bone(__WarpCommon):
    target: str = field(init=False)

    def __call__(self, state: State) -> None:
        self.target = state.bonfire
        super().__call__(state)
        state.items["Homeward Bone"] -= 1


@dataclass
class Darksign(__WarpCommon):
    target: str = ""  # override

    def __call__(self, state: State) -> None:
        self.target = state.bonfire
        super().__call__(state)
        state.souls = 0


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
    ...  # class only exists to rename the action in __str__


@dataclass(kw_only=True)
class Loot(Action):
    bank: int = 0
    count: int = 1

    @property
    def display(self) -> str:
        output = self.target
        if self.count > 1:
            output += f" (x{self.count})"
        return output

    def __call__(self, state: State) -> None:
        state.items[self.target] += self.count
        state.bank += self.bank * self.count


class Use(Loot):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.bank *= -1


@dataclass
class Receive(Loot):
    ...  # class only exists to rename the action in __str__


@dataclass(kw_only=True)
class Kill(Action):
    souls: int
    count: int = 1

    def __call__(self, state: State) -> None:
        state.souls += self.souls * self.count


@dataclass
class AutoKill(Kill):
    ...  # class only exists to rename the action in __str__


@dataclass(kw_only=True)
class Buy(Kill):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.souls *= -1

    def __call__(self, state: State) -> None:
        super().__call__(state)
        state.items[self.target] += self.count


@dataclass
class Run(Action):
    def __call__(self, state: State) -> None:
        ...


@dataclass
class Jump(Run):
    ...  # class only exists to rename the action in __str__


@dataclass
class Activate(Action):
    def __call__(self, state: State) -> None:
        ...


@dataclass
class Talk(Activate):
    ...  # class only exists to rename the action in __str__
