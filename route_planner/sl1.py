from __future__ import annotations

from .action import (
    Activate,
    AutoBonfire,
    AutoEquip,
    AutoKill,
    BonfireSit,
    Buy,
    Equip,
    Heal,
    Item,
    Jump,
    Kill,
    Loot,
    Perform,
    Receive,
    Region,
    Run,
    TakeDamage,
    Talk,
    UnEquip,
    Use,
    UseMenu,
)
from .route import Segment


class InitialState(Segment):
    def __init__(self):
        detail = "starting equipment"
        super().__init__(
            Loot(Item.DARKSIGN, detail=detail),
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
            Loot(Item.BONE, count=6, detail="hidden chest"),
            Equip(Item.BONE, "Item 5", detail="immediately"),
            Loot(
                "Large Soul of a Lost Undead",
                bank=400,
                detail="middle of graveyard",
            ),
            Loot(
                "Large Soul of a Lost Undead",
                bank=400,
                detail="start of graveyard",
            ),
            Use(Item.BONE),
        )


class FetchReinforcedClub(Segment):
    def __init__(self):
        super().__init__(
            Region("Undead Burg"),
            Buy("Reinforced Club", souls=350, detail="Undead Merchant"),
            Buy(
                "Firebomb",
                souls=50,
                count=3,
                detail="Undead Merchant, if using Tohki Bombs on Bed of Chaos",
                optional=True,
            ),
            Use(Item.BONE),
        )


class FirelinkToAndre(Segment):
    def __init__(self):
        new_londo_elevator = "on elevator to New Londo Ruins"
        basin_elevator = "on elevator to Darkroot Basin"
        ladder = "climbing ladder to RTSR"
        super().__init__(
            Region("Firelink Shrine"),
            UseMenu(
                "Large Soul of a Lost Undead",
                count=2,
                detail=new_londo_elevator,
            ),
            UseMenu("Soul of a Lost Undead", detail=new_londo_elevator),
            Region("New Londo Ruins"),
            Loot(
                "Soul of a Nameless Soldier",
                bank=800,
                detail="by new londo elevator",
            ),
            Region("Valley of Drakes"),
            Loot(
                "Large Soul of a Nameless Soldier",
                bank=1000,
                detail="behind master key door",
            ),
            TakeDamage(
                "falling off ledge above Ancient Dragon",
                detail="RTSR setup (1/3)",
            ),
            Loot("Soul of a Proud Knight", bank=2000, detail="by dragon"),
            Equip("Reinforced Club", "Right Hand", detail=ladder),
            Equip("Soul of a Nameless Soldier", "Item 2", detail=ladder),
            Equip("Large Soul of a Nameless Soldier", "Item 3", detail=ladder),
            Equip("Soul of a Proud Knight", "Item 4", detail=ladder),
            Loot("Red Tearstone Ring"),
            TakeDamage(
                "falling off ledge by Red Tearstone Ring",
                detail="RTSR setup (2/3)",
            ),
            Use("Soul of a Nameless Soldier", detail=basin_elevator),
            Use("Large Soul of a Nameless Soldier", detail=basin_elevator),
            Use("Soul of a Proud Knight", detail=basin_elevator),
            Equip("Red Tearstone Ring", "Ring 2", detail=basin_elevator),
            Region("Darkroot Basin"),
            Loot("Grass Crest Shield"),
            Equip("Grass Crest Shield", "Left Hand", detail="immediately"),
            Kill("Black Knight", souls=1800, detail="by Grass Crest Shield"),
        )


class NormalUpgradeWeaponPlus5(Segment):
    def __init__(self):
        super().__init__(
            Region("Undead Parish"),
            Buy("Titanite Shard", count=9, souls=800, detail="Andre"),
            Buy("Normal Upgrade Weapon", count=5, souls=200, detail="Andre"),
        )


class AndreToGargoyles(Segment):
    def __init__(self):
        super().__init__(
            Region("Undead Parish"),
            TakeDamage(
                "falling off right-side ledge above Basement key",
                detail="RTSR setup (3/3)",
            ),
            Loot("Basement Key", detail="by gate lever"),
            Activate(
                "Elevator to Firelink Shrine", detail="just run, don't roll"
            ),
            Kill("Gargoyles", souls=10000),
            Activate("First bell"),
            Use(Item.BONE),
        )


class FirelinkToQuelaag(Segment):
    def __init__(self):
        super().__init__(
            Region("Firelink Shrine"),
            Kill(
                "Lautrec",
                souls=1000,
                detail="kick off ledge, with bare hands for safety",
            ),
            Run("to back entrance to Blighttown"),
            Region("Blighttown"),
            Perform("Blighttown drop"),
            Kill(
                "Blowdart Sniper",
                souls=600,
                detail="run off ledge and plunging attack",
            ),
            Receive("Purple Moss", detail="Blowdart Snper"),
            Heal("using Estus Flask", detail="on waterwheel"),
            TakeDamage(
                "falling off waterwheel onto scaffold and then off that too",
                detail="RTSR setup, swamp poison finishes the job",
            ),
            UseMenu(
                "Purple Moss", detail="once in RTSR range and out of swamp"
            ),
            Kill("Quelaag", souls=20000),
            Receive("Soul of Quelaag", bank=8000, detail="Quelaag"),
            Activate("Second bell"),
            Receive(Item.BONE, detail="Second bell"),
            Use(Item.BONE),
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
            NormalUpgradeWeaponPlus5(),
            AndreToGargoyles(),
            FirelinkToQuelaag(),
        ]:
            self += segment
