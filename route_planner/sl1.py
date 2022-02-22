from __future__ import annotations

from .action import (
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
    Warp,
)
from .route import Segment, Route


class StartOfGame(Segment):
    def __init__(self):
        super().__init__()
        self.add_actions(
            Region("Northern Undead Asylum"),
            AutoBonfire("Undead Asylum Dungeon Cell"),
        )


class PyromancerInitialState(Segment):
    def __init__(self):
        super().__init__()
        detail = "Pyromancer starting equipment"
        self.add_actions(
            Equip("Straight Sword Hilt", "Right Hand", detail=detail),
            Equip("Tattered Cloth Hood", "Head", detail=detail),
            Equip("Tattered Cloth Robe", "Torso", detail=detail),
            Equip("Tattered Cloth Manchette", "Arms", detail=detail),
            Equip("Heavy Boots", "Legs", detail=detail),
        )


class AsylumCellToFirelink(Segment):
    def __init__(self):
        super().__init__()
        self.add_actions(
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
        )


class FirelinkLoot(Segment):
    def __init__(self, *, elevator_soul: bool, graveyard_souls: int):
        super().__init__()
        self.add_actions(Region("Firelink Shrine"))
        if elevator_soul:
            self.add_actions(
                Loot(
                    "Soul of a Lost Undead", bank=200, detail="upper elevator"
                ),
                Jump("off ledge to hidden chests"),
            )
        else:
            self.add_actions(Run("under upper elevator"))

        self.add_actions(
            Loot("Homeward Bone", count=6, detail="hidden chest"),
            Equip("Homeward Bone", "Item 5", detail="immediately"),
        )

        if not (0 <= graveyard_souls <= 2):
            raise ValueError(
                f"graveyard_souls not within valid range: {graveyard_souls}"
            )
        if graveyard_souls:
            graveyard_souls -= 1
            self.add_actions(
                Loot(
                    "Large Soul of a Lost Undead",
                    bank=400,
                    detail="middle graveyard",
                )
            )
        if graveyard_souls:
            graveyard_souls -= 1
            self.add_actions(
                Loot(
                    "Large Soul of a Lost Undead",
                    bank=400,
                    detail="start of graveyard",
                )
            )


class FetchReinforcedClub(Segment):
    def __init__(self):
        super().__init__()
        self.add_actions(
            Region("Undead Burg"),
            Buy("Reinforced Club", detail="Undead Merchant", souls=350),
            Bone(),
        )


class SL1MeleeOnlyGlitchless(Route):
    def __init__(self):
        super().__init__()
        self.add_segments(
            PyromancerInitialState(),
            StartOfGame(),
            AsylumCellToFirelink(),
            FirelinkLoot(elevator_soul=True, graveyard_souls=2),
            FetchReinforcedClub(),
        )
