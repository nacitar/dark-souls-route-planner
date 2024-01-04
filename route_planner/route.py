from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Callable, Generator, Optional

from .action import Event, State, Step


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


@dataclass(kw_only=True)
class Segment:  # is a 'action.Step'
    notes: list[str] = field(default_factory=list)
    condition: bool = True
    condition_callback: Callable[[State], bool] = lambda state: True
    # not in init to force using the varargs add_steps, so call sites are less
    # indented by not having to specify the nested list.
    steps: list[Step] = field(default_factory=list, init=False)

    def __post_init__(self) -> None:
        pass

    def add_steps(self, *steps: Step) -> Segment:
        self.steps.extend(steps)
        return self

    def generate_events(self, state: State) -> Generator[Event, None, None]:
        if self.condition and self.condition_callback(state):
            state.notes.extend(self.notes)
            for step in self.steps:
                yield from step.generate_events(state)


@dataclass(kw_only=True)
class RouteData:
    events: list[Event] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class Route:
    name: str
    segment: Segment
    damage_tables: list[DamageTable] = field(default_factory=list)
    hit_lookup: Optional[dict[str, dict[Enemy, dict[HitType, Hit]]]] = None

    def run(self, *, state: Optional[State] = None) -> RouteData:
        if not state:
            state = State()
        route_data = RouteData()
        for event in self.segment.generate_events(state):
            route_data.events.append(event)
        route_data.notes = state.notes
        return route_data
