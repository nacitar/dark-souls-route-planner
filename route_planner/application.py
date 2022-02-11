from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import chain
from typing import Iterable, Optional

from .event import (
    Activate,
    BonfireAuto,
    BonfireSit,
    Buy,
    Darksign,
    Equip,
    EquipAuto,
    Event,
    HomewardBone,
    Kill,
    KillAuto,
    Loot,
    LootSoul,
    Metrics,
    Receive,
    Region,
    State,
    Talk,
    UnEquip,
    Warp,
)


@dataclass(frozen=True)
class Output:
    metrics: Metrics
    event: Event


class Route:
    def __init__(self, *, state: Optional[State] = None):
        if state is None:
            state = State()
        self.state = state
        self.output: list[Output] = []
        if self.state.region:
            self.add([Region(self.state.region)])

    def add(self, event_group: Iterable[Event]):
        for event in event_group:
            event(self.state)
            self.state.metrics = replace(  # creates a copy
                self.state.metrics, bones=self.state.items["Homeward Bone"]
            )
            self.output.append(Output(metrics=self.state.metrics, event=event))

    def extend(self, event_groups: Iterable[Iterable[Event]]):
        for event_group in event_groups:
            self.add(event_group)


def start_of_game() -> Iterable[Event]:
    return [
        Region("Northern Undead Asylum"),
        BonfireAuto("Undead Asylum Dungeon Cell"),
    ]


def pyromancer_initial_state() -> Iterable[Event]:
    notes = "Pyromancer starting equipment"
    return [
        Equip("Straight Sword Hilt", "Right Hand", notes=notes),
        Equip("Tattered Cloth Hood", "Head", notes=notes),
        Equip("Tattered Cloth Robe", "Torso", notes=notes),
        Equip("Tattered Cloth Manchette", "Arms", notes=notes),
        Equip("Heavy Boots", "Legs", notes=notes),
    ]


def asylum_cell_to_firelink() -> Iterable[Event]:
    return chain(
        pyromancer_initial_state(),
        [
            Loot("Dungeon Cell Key"),
            UnEquip("Torso", location="First ladder or big door."),
            UnEquip("Arms", location="First ladder or big door."),
            Loot("Hand Axe"),
            Equip("Hand Axe", "Right Hand", location="Fog gate before Oscar"),
            Talk("Oscar of Astora", location="Behind wall boulder breaks"),
            Receive("Estus Flask", location="Oscar of Astora"),
            EquipAuto("Estus Flask", "Item 0"),
            Receive("Undead Asylum F2 East Key", location="Oscar of Astora"),
            KillAuto("Oscar of Astora", souls=100),
            Kill("Asylum Demon", souls=2000),
            Receive("Big Pilgrim's Key", location="Asylum Demon"),
            Activate("Big Pilgrim's Key Door", location="Asylum Demon"),
            Activate("Ledge warp trigger to Firelink Shrine"),
            Region("Firelink Shrine"),
            BonfireAuto("Firelink Shrine"),
        ],
    )


def firelink_early_loot() -> Iterable[Event]:
    return [
        Region("Firelink Shrine"),
        LootSoul(
            "Soul of a Lost Undead", location="by elevator to Undead Parish"
        ),
        Loot(
            "Homeward Bone",
            count=6,
            location="chest reached via under elevator",
        ),
        Equip("Homeward Bone", "Item 5", location="immediately after looting"),
        LootSoul(
            "Large Soul of a Lost Undead", location="middle of graveyard"
        ),
        LootSoul("Large Soul of a Lost Undead", location="start of graveyard"),
        HomewardBone(),
    ]


def fetch_reinforced_club() -> Iterable[Event]:
    return [
        Region("Undead Burg"),
        Buy("Reinforced Club", location="Undead Merchant", souls=350),
        HomewardBone(),
        Region("Firelink Shrine"),
    ]


class SL1MeleeOnlyGlitchless(Route):
    def __init__(self):
        super().__init__()
        self.add(
            chain(
                start_of_game(),
                pyromancer_initial_state(),
                asylum_cell_to_firelink(),
                firelink_early_loot(),
                fetch_reinforced_club(),
            )
        )


def main() -> int:
    route = SL1MeleeOnlyGlitchless()
    for entry in route.output:
        print(entry)

    return 0
