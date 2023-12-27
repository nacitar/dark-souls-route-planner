from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Generator, Optional, Protocol, Tuple

from .action import Action, Error, State


@dataclass
class Hit:
    damage: int = 0
    with_rtsr: int = field(default=0, kw_only=True)


@dataclass
class HitTypeInfo:
    display_name: str
    column_name: str = field(kw_only=True)


@unique
class HitType(Enum):
    # this is ordered from weakest to strongest
    WEAK_1H = HitTypeInfo("Weak(1H)", column_name="Wk1H")
    HEAVY_1H = HitTypeInfo("Heavy(1H)", column_name="Hvy1H")
    WEAK_2H = HitTypeInfo("Weak(2H)", column_name="Wk2H")
    JUMPING_1H = HitTypeInfo("Jumping(1H)", column_name="Jmp1H")
    HEAVY_2H = HitTypeInfo("Heavy(2H)", column_name="Hvy2H")
    JUMPING_2H = HitTypeInfo("Jumping(2H)", column_name="Jmp2H")
    BACKSTAB_1H = HitTypeInfo("Backstab(1H)", column_name="Bs1H")
    BACKSTAB_2H = HitTypeInfo("Backstab(2H)", column_name="Bs2H")
    RIPOSTE_1H = HitTypeInfo("Riposte(1H)", column_name="Rip1H")
    RIPOSTE_2H = HitTypeInfo("Riposte(2H)", column_name="Rip2H")

    @property  # not needed, but reads better in the code
    def info(self) -> HitTypeInfo:
        return self.value


@dataclass(kw_only=True)
class EnemyInfo:
    form_health_lookup: dict[str, int]


@unique
class Enemy(Enum):
    BLACK_KNIGHT_DARKROOT_BASIN = EnemyInfo(
        form_health_lookup={"Black Knight (Darkroot Basin)": 603}
    )
    BELL_GARGOYLES = EnemyInfo(
        form_health_lookup={"Bell Gargoyle 1": 999, "Bell Gargoyle 2": 480}
    )
    OSWALD = EnemyInfo(form_health_lookup={"Oswald of Carim": 638})
    PETRUS = EnemyInfo(form_health_lookup={"Petrus of Thorolund": 594})
    LAUTREC = EnemyInfo(form_health_lookup={"Knight Lautrec of Carim": 862})
    QUELAAG = EnemyInfo(form_health_lookup={"Chaos Witch Quelaag": 3139})
    IRON_GOLEM = EnemyInfo(
        form_health_lookup={
            "Iron Golem": 2880,
            "Iron Golem (stagger)": 400,
            "Iron Golem (fall)": 200,
        }
    )
    GIANT_BLACKSMITH = EnemyInfo(form_health_lookup={"Giant Blacksmith": 1812})
    MIMIC_OCCULT_CLUB = EnemyInfo(
        form_health_lookup={"Mimic (Occult Club)": 1041}
    )
    DARKMOON_KNIGHTESS = EnemyInfo(
        form_health_lookup={"Darkmoon Knightess": 719}
    )

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
    notes: list[str] = field(default_factory=list)
    condition: bool = True
    # actions not available in init so add_steps can check step.condition
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


@dataclass
class Route:
    name: str
    segment: Segment
    damage_tables: list[DamageTable] = field(default_factory=list)
    hit_lookup: Optional[dict[str, dict[Enemy, dict[HitType, Hit]]]] = None
