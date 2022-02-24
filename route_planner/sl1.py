from __future__ import annotations

from .action import (
    BONE_ITEM,
    DARKSIGN_ITEM,
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
    UseMenu,
    Warp,
)
from .route import Segment


class InitialState(Segment):
    def __init__(self):
        detail = "starting equipment"
        super().__init__(
            Loot(DARKSIGN_ITEM, detail=detail),
            Loot("Straight Sword Hilt", detail=detail),
            Equip("Straight Sword Hilt", "Right Hand", detail=detail),
        )


class PyromancerInitialState(Segment):
    def __init__(self):
        detail = "Pyromancer starting equipment"
        super().__init__(
            Loot("Tattered Cloth Hood", detail=detail),
            Loot("Tattered Cloth Robe", detail=detail),
            Loot("Tattered Cloth Manchette", detail=detail),
            Loot("Heavy Boots", detail=detail),
            Equip("Tattered Cloth Hood", "Head", detail=detail),
            Equip("Tattered Cloth Robe", "Torso", detail=detail),
            Equip("Tattered Cloth Manchette", "Arms", detail=detail),
            Equip("Heavy Boots", "Legs", detail=detail),
        )


class StartOfGame(Segment):
    def __init__(self):
        super().__init__(
            Region("Northern Undead Asylum"),
            AutoBonfire("Undead Asylum Dungeon Cell"),
        )


class AsylumCellToFirelink(Segment):
    def __init__(self):
        super().__init__(
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
    def __init__(self):
        super().__init__(
            Region("Firelink Shrine"),
            Loot("Soul of a Lost Undead", bank=200, detail="upper elevator"),
            Jump("off ledge to hidden chests"),
            Loot(BONE_ITEM, count=6, detail="hidden chest"),
            Equip(BONE_ITEM, "Item 5", detail="immediately"),
            Loot(
                "Large Soul of a Lost Undead",
                bank=400,
                detail="middle graveyard",
            ),
            Loot(
                "Large Soul of a Lost Undead",
                bank=400,
                detail="start of graveyard",
            ),
            Bone(),
        )


class FetchReinforcedClub(Segment):
    def __init__(self):
        super().__init__(
            Region("Undead Burg"),
            Buy("Reinforced Club", detail="Undead Merchant", souls=350),
            Bone(),
        )


class FirelinkToAndre(Segment):
    def __init__(self):
        elevator = "new londo ruins elevator"
        super().__init__(
            Region("Firelink Shrine"),
            UseMenu("Large Soul of a Lost Undead", count=2, detail=elevator),
            UseMenu("Soul of a Lost Undead", detail=elevator),
            Equip("Reinforced Club", "Right Hand", detail=elevator),
            Region("New Londo Ruins"),
            Loot("Soul of a Nameless Soldier", bank=800, detail="by elevator"),
            Region("Valley of Drakes"),
            Loot("Large Soul of a Nameless Soldier", bank=1000, detail="behind master key door"),
            Loot("Soul of a Proud Knight", bank=2000, detail="by dragon"),
            Equip("Soul of a Nameless Soldier", "Item 2"),
            Equip("Large Soul of a Nameless Soldier", "Item 3"),
            Equip("Soul of a Proud Knight", "Item 4"),
            Use("Soul of a Nameless Soldier"),
            Use("Large Soul of a Nameless Soldier"),
            Use("Soul of a Proud Knight"),
        )



class SL1MeleeOnlyGlitchless(Segment):
    def __init__(self):
        super().__init__()
        for segment in [
            InitialState(),
            PyromancerInitialState(),
            StartOfGame(),
            AsylumCellToFirelink(),
            FirelinkLoot(),
            FetchReinforcedClub(),
            FirelinkToAndre(),
        ]:
            self += segment
