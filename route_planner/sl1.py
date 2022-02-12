from __future__ import annotations

from typing import Iterable

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
    Jump,
    Kill,
    KillAuto,
    Loot,
    LootSoul,
    Receive,
    Region,
    Run,
    Talk,
    UnEquip,
    Warp,
)
from .route import Entry, Route


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
    return [
        Region("Northern Undead Asylum"),
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
    ]


def firelink_loot(
    *, elevator_soul: bool, graveyard_souls: int
) -> Iterable[Event]:
    events: list[Event] = [Region("Firelink Shrine")]
    if elevator_soul:
        events.extend(
            [
                LootSoul("Soul of a Lost Undead", location="upper elevator"),
                Jump("off ledge to hidden chests"),
            ]
        )
    else:
        events.extend([Run("under upper elevator")])

    events.extend(
        [
            Loot("Homeward Bone", count=6, location="hidden chest"),
            Equip("Homeward Bone", "Item 5", location="immediately"),
        ]
    )

    all_graveyard_soul_events = [
        LootSoul("Large Soul of a Lost Undead", location="middle graveyard"),
        LootSoul("Large Soul of a Lost Undead", location="start of graveyard"),
    ]
    if 0 <= graveyard_souls <= 2:
        events.extend(all_graveyard_soul_events[0:graveyard_souls])
    else:
        raise ValueError(
            f"graveyard_souls must be in range [0,2] but is {graveyard_souls}"
        )

    events.append(HomewardBone())
    return events


def fetch_reinforced_club() -> Iterable[Event]:
    return [
        Region("Undead Burg"),
        Buy("Reinforced Club", location="Undead Merchant", souls=350),
        HomewardBone(),
    ]


class SL1MeleeOnlyGlitchless(Route):
    def __init__(self):
        super().__init__()
        self.extend(
            [
                start_of_game(),
                pyromancer_initial_state(),
                asylum_cell_to_firelink(),
                firelink_loot(elevator_soul=True, graveyard_souls=2),
                fetch_reinforced_club(),
            ]
        )
