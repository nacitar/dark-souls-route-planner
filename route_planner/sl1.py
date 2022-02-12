from __future__ import annotations

from typing import Iterable

from .action import (
    Activate,
    BonfireAuto,
    BonfireSit,
    Buy,
    Darksign,
    Equip,
    EquipAuto,
    Action,
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


def start_of_game() -> Iterable[Action]:
    return [
        Region("Northern Undead Asylum"),
        BonfireAuto("Undead Asylum Dungeon Cell"),
    ]


def pyromancer_initial_state() -> Iterable[Action]:
    detail = "Pyromancer starting equipment"
    return [
        Equip("Straight Sword Hilt", "Right Hand", detail=detail),
        Equip("Tattered Cloth Hood", "Head", detail=detail),
        Equip("Tattered Cloth Robe", "Torso", detail=detail),
        Equip("Tattered Cloth Manchette", "Arms", detail=detail),
        Equip("Heavy Boots", "Legs", detail=detail),
    ]


def asylum_cell_to_firelink() -> Iterable[Action]:
    return [
        Region("Northern Undead Asylum"),
        Loot("Dungeon Cell Key"),
        UnEquip("Torso", detail="First ladder or big door."),
        UnEquip("Arms", detail="First ladder or big door."),
        Loot("Hand Axe"),
        Equip("Hand Axe", "Right Hand", detail="Fog gate before Oscar"),
        Talk("Oscar of Astora", detail="Behind wall boulder breaks"),
        Receive("Estus Flask", detail="Oscar of Astora"),
        EquipAuto("Estus Flask", "Item 0"),
        Receive("Undead Asylum F2 East Key", detail="Oscar of Astora"),
        KillAuto("Oscar of Astora", souls=100),
        Kill("Asylum Demon", souls=2000),
        Receive("Big Pilgrim's Key", detail="Asylum Demon"),
        Activate("Big Pilgrim's Key Door", detail="Asylum Demon"),
        Activate("Ledge warp trigger to Firelink Shrine"),
        Region("Firelink Shrine"),
        BonfireAuto("Firelink Shrine"),
    ]


def firelink_loot(
    *, elevator_soul: bool, graveyard_souls: int
) -> Iterable[Action]:
    actions: list[Action] = [Region("Firelink Shrine")]
    if elevator_soul:
        actions.extend(
            [
                LootSoul("Soul of a Lost Undead", detail="upper elevator"),
                Jump("off ledge to hidden chests"),
            ]
        )
    else:
        actions.extend([Run("under upper elevator")])

    actions.extend(
        [
            Loot("Homeward Bone", count=6, detail="hidden chest"),
            Equip("Homeward Bone", "Item 5", detail="immediately"),
        ]
    )

    all_graveyard_soul_actions = [
        LootSoul("Large Soul of a Lost Undead", detail="middle graveyard"),
        LootSoul("Large Soul of a Lost Undead", detail="start of graveyard"),
    ]
    if 0 <= graveyard_souls <= 2:
        actions.extend(all_graveyard_soul_actions[0:graveyard_souls])
    else:
        raise ValueError(
            f"graveyard_souls must be in range [0,2] but is {graveyard_souls}"
        )

    actions.append(HomewardBone())
    return actions


def fetch_reinforced_club() -> Iterable[Action]:
    return [
        Region("Undead Burg"),
        Buy("Reinforced Club", detail="Undead Merchant", souls=350),
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
