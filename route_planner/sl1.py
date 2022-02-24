from __future__ import annotations

from typing import Iterable

from .action import (
    Action,
    Activate,
    AutoBonfire,
    AutoEquip,
    AutoKill,
    Bone,
    BonfireSit,
    Buy,
    Darksign,
    Equip,
    Jump,
    Kill,
    Loot,
    Receive,
    Region,
    Run,
    Talk,
    UnEquip,
    Use,
    Warp,
)
from .route import Route


def start_of_game() -> Iterable[Action]:
    yield from [
        Region("Northern Undead Asylum"),
        AutoBonfire("Undead Asylum Dungeon Cell"),
    ]


def pyromancer_initial_state() -> Iterable[Action]:
    detail = "Pyromancer starting equipment"
    yield from [
        Loot("Straight Sword Hilt"),
        Loot("Tattered Cloth Hood"),
        Loot("Tattered Cloth Robe"),
        Loot("Tattered Cloth Manchette"),
        Loot("Heavy Boots"),
        Equip("Straight Sword Hilt", "Right Hand", detail=detail),
        Equip("Tattered Cloth Hood", "Head", detail=detail),
        Equip("Tattered Cloth Robe", "Torso", detail=detail),
        Equip("Tattered Cloth Manchette", "Arms", detail=detail),
        Equip("Heavy Boots", "Legs", detail=detail),
    ]


def asylum_cell_to_firelink() -> Iterable[Action]:
    yield from [
        Region("Northern Undead Asylum"),
        Loot("Dungeon Cell Key"),
        UnEquip("Torso", detail="First ladder or big door."),
        UnEquip("Arms", detail="First ladder or big door."),
        Loot("Hand Axe"),
        Equip("Hand Axe", "Right Hand", detail="Fog gate before Oscar"),
        Talk("Oscar of Astora", detail="Behind wall boulder breaks"),
        Receive("Estus Flask", detail="Oscar of Astora"),
        AutoEquip("Estus Flask", "Item 0"),
        Receive("Undead Asylum F2 East Key", detail="Oscar of Astora"),
        AutoKill("Oscar of Astora", souls=100),
        Kill("Asylum Demon", souls=2000),
        Receive("Big Pilgrim's Key", detail="Asylum Demon"),
        Activate("Big Pilgrim's Key Door", detail="Asylum Demon"),
        Activate("Ledge warp trigger to Firelink Shrine"),
        Region("Firelink Shrine"),
        AutoBonfire("Firelink Shrine"),
    ]


def firelink_loot(
    *, elevator_soul: bool, graveyard_souls: int
) -> Iterable[Action]:
    yield Region("Firelink Shrine")
    if elevator_soul:
        yield from [
            Loot("Soul of a Lost Undead", bank=200, detail="upper elevator"),
            Jump("off ledge to hidden chests"),
        ]
    else:
        yield Run("under upper elevator")
    yield from [
        Loot("Homeward Bone", count=6, detail="hidden chest"),
        Equip("Homeward Bone", "Item 5", detail="immediately"),
    ]

    if not (0 <= graveyard_souls <= 2):
        raise ValueError(
            f"graveyard_souls not within valid range: {graveyard_souls}"
        )
    if graveyard_souls:
        graveyard_souls -= 1
        yield Loot(
            "Large Soul of a Lost Undead", bank=400, detail="middle graveyard"
        )
    if graveyard_souls:
        graveyard_souls -= 1
        yield Loot(
            "Large Soul of a Lost Undead",
            bank=400,
            detail="start of graveyard",
        )
    yield Bone()


def fetch_reinforced_club() -> Iterable[Action]:
    yield from [
        Region("Undead Burg"),
        Buy("Reinforced Club", detail="Undead Merchant", souls=350),
        Bone(),
    ]


def firelink_to_andre() -> Iterable[Action]:
    yield from [
        Region("Firelink Shrine"),
        Use(
            "Large Soul of a Lost Undead",
            count=2,
            detail="new londo ruins elevator",
        ),
        Use("Soul of a Lost Undead", detail="new londo ruins elevator"),
    ]


class SL1MeleeOnlyGlitchless(Route):
    def __init__(self):
        super().__init__(
            pyromancer_initial_state(),
            start_of_game(),
            asylum_cell_to_firelink(),
            firelink_loot(elevator_soul=True, graveyard_souls=2),
            fetch_reinforced_club(),
            firelink_to_andre(),
        )
