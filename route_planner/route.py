from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum, unique
from math import ceil
from typing import Generator, Optional, Protocol, Tuple

from .action import Action, Error, State


@dataclass
class Damage:
    value: int = 0
    with_rtsr: int = field(default=0, kw_only=True)


@dataclass
class HitTypeInfo:
    display_name: str
    column_name: str = field(kw_only=True)


@unique
class HitType(Enum):
    RIPOSTE_2H = HitTypeInfo("Riposte (2H)", column_name="R(2H)")
    RIPOSTE_1H = HitTypeInfo("Riposte (1H)", column_name="R(1H)")
    HEAVY = HitTypeInfo("Heavy", column_name="Heavy")
    WEAK = HitTypeInfo("Weak", column_name="Weak")

    @property  # not needed, but reads better in the code
    def info(self) -> HitTypeInfo:
        return self.value


@dataclass
class EnemyInfo:
    display_name: str
    health: int = field(kw_only=True)

    def hits(self, *, damage: int) -> int:
        return ceil(self.health / damage)


@unique
class Enemy(Enum):
    BLACK_KNIGHT_DARKROOT_BASIN = EnemyInfo(
        "Black Knight (Darkroot Basin)", health=603
    )
    BELL_GARGOYLE_A = EnemyInfo("Bell Gargoyle A", health=999)
    BELL_GARGOYLE_B = EnemyInfo("Bell Gargoyle A", health=480)
    QUELAAG = EnemyInfo("Chaos Witch Quelaag", health=3139)
    IRON_GOLEM_STAGGER = EnemyInfo("Iron Golem stagger", health=400)
    IRON_GOLEM_FALL = EnemyInfo("Iron Golem fall", health=200)
    IRON_GOLEM = EnemyInfo("Iron Golem", health=2880)
    GIANT_BLACKSMITH = EnemyInfo("Giant Blacksmith", health=1812)

    @property  # not needed, but reads better in the code
    def info(self) -> EnemyInfo:
        return self.value


@dataclass(kw_only=True)
class DamageTable:
    weapon: str
    enemies: list[Enemy]
    hit_types: list[HitType] = field(default_factory=lambda: list(HitType))


class Step(Protocol):
    @property
    def actions(self) -> list[Action]:
        ...

    @property
    def notes(self) -> list[str]:
        ...

    @property
    def condition(self) -> bool:
        ...


@dataclass(kw_only=True)
class Segment:  # is a 'Step'
    name: str = ""
    notes: list[str] = field(default_factory=list)
    condition: bool = True
    actions: list[Action] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        if not self.condition:
            self.notes = []

    def add_steps(self, *steps: Step) -> Segment:
        for step in steps:
            if step.condition:
                self.notes.extend(step.notes)
                self.actions.extend(step.actions)
        return self

    def process(
        self, state: Optional[State] = None
    ) -> Generator[Tuple[State, Action], None, None]:
        if state is None:
            state = State()
        for action in self.actions:
            action = deepcopy(action)  # so actions can modify themselves
            action(state)
            yield (deepcopy(state), action)
            for error in state.errors():
                yield (deepcopy(state), Error(error))


def conditional(
    condition: bool, *steps: Step, notes: Optional[list[str]] = None
) -> Segment:
    if not condition:
        return Segment()
    return Segment(notes=notes if notes else []).add_steps(*steps)


@dataclass
class Route:
    name: str
    segment: Segment
    damage_tables: list[DamageTable] = field(default_factory=list)
    damage_lookup: Optional[
        dict[str, dict[Enemy, dict[HitType, Damage]]]
    ] = None
