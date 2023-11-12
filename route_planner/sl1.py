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
    RunTo,
    FallDamage,
    Talk,
    UnEquip,
    Use,
    UseMenu,
    WaitFor,
)
from .route import Segment

new_londo_elevator = "elevator to New Londo Ruins"
basin_elevator = "elevator to Darkroot Basin"
parish_elevator = "elevator to Undead Parish"


class InitialState(Segment):
    def __init__(self):
        detail = "starting equipment"
        super().__init__(
            Receive(Item.DARKSIGN, detail=detail),
            Receive("Straight Sword Hilt", detail=detail),
            AutoEquip("Straight Sword Hilt", "Right Hand", detail=detail),
        )


class PyromancerInitialState(Segment):
    def __init__(self):
        detail = "Pyromancer starting equipment"
        super().__init__(
            Receive("Tattered Cloth Hood", detail=detail),
            Receive("Tattered Cloth Robe", detail=detail),
            Receive("Tattered Cloth Manchette", detail=detail),
            Receive("Heavy Boots", detail=detail),
            AutoEquip("Tattered Cloth Hood", "Head", detail=detail),
            AutoEquip("Tattered Cloth Robe", "Torso", detail=detail),
            AutoEquip("Tattered Cloth Manchette", "Arms", detail=detail),
            AutoEquip("Heavy Boots", "Legs", detail=detail),
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
            Loot(Item.HUMANITY, count=3, humanities=1, detail="side of well"),
            Loot("Soul of a Lost Undead", souls=200, detail="upper elevator"),
            Jump("off ledge to hidden chests"),
            Loot(Item.BONE, count=6, detail="hidden chest"),
            Equip(Item.BONE, "Item 5", detail="immediately"),
            Loot(
                "Large Soul of a Lost Undead",
                souls=400,
                detail="middle of graveyard",
            ),
            Loot(
                "Large Soul of a Lost Undead",
                souls=400,
                detail="start of graveyard",
            ),
            Use(Item.BONE),
        )


class FirelinkToReinforcedClub(Segment):
    def __init__(self):
        super().__init__(
            Region("Firelink Shrine"),
            RunTo("Undead Burg"),
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
        ladder = "climbing ladder to RTSR"
        super().__init__(
            Region("Firelink Shrine"),
            RunTo(new_londo_elevator),
            UseMenu(
                "Large Soul of a Lost Undead",
                count=2,
                detail=new_londo_elevator,
            ),
            UseMenu("Soul of a Lost Undead", detail=new_londo_elevator),
            Region("New Londo Ruins"),
            Loot(
                "Soul of a Nameless Soldier",
                souls=800,
                detail=f"by bottom of {new_londo_elevator}",
            ),
            Region("Valley of Drakes"),
            Loot(
                "Large Soul of a Nameless Soldier",
                souls=1000,
                detail="behind master key door",
            ),
            FallDamage("ledge above Undead Dragon", detail="RTSR setup (1/3)"),
            Loot(
                "Soul of a Proud Knight",
                souls=2000,
                detail="last item by Undead Dragon",
            ),
            Equip("Reinforced Club", "Right Hand", detail=ladder),
            Equip("Soul of a Nameless Soldier", "Item 2", detail=ladder),
            Equip("Large Soul of a Nameless Soldier", "Item 3", detail=ladder),
            Equip("Soul of a Proud Knight", "Item 4", detail=ladder),
            Loot("Red Tearstone Ring"),
            FallDamage(
                "ledge by Red Tearstone Ring", detail="RTSR setup (2/3)"
            ),
            RunTo(basin_elevator),
            Use("Soul of a Nameless Soldier", detail=basin_elevator),
            Use("Large Soul of a Nameless Soldier", detail=basin_elevator),
            Use("Soul of a Proud Knight", detail=basin_elevator),
            Equip("Red Tearstone Ring", "Ring 2", detail=basin_elevator),
            Region("Darkroot Basin"),
            Loot("Grass Crest Shield"),
            Equip("Grass Crest Shield", "Left Hand", detail="immediately"),
            Kill("Black Knight", souls=1800, detail="by Grass Crest Shield"),
            RunTo("Undead Parish"),
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
            RunTo("gate area by Basement Key"),
            FallDamage(
                "right-side ledge above Basement key",
                detail="RTSR setup (3/3)",
            ),
            Loot("Basement Key", detail="by gate lever"),
            Loot(
                "Fire Keeper Soul",
                humanities=5,
                detail="on altar behind Berenike Knight",
            ),
            Activate(
                "Elevator to Firelink Shrine", detail="just run, don't roll"
            ),
            Kill("Bell Gargoyles", souls=10000),
            Receive(
                Item.TWIN_HUMANITIES, humanities=2, detail="Bell Gargoyles"
            ),
            Activate("First bell"),
            RunTo(
                "Oswald of Carim",
                detail="RTSR setup: heal, fall down both ladders",
            ),
            Kill("Oswald of Carim", souls=2000, detail="can buy bones here"),
            Loot(
                Item.TWIN_HUMANITIES,
                count=2,
                humanities=2,
                detail="Oswald of Carim",
            ),
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
            Loot(
                Item.HUMANITY,
                count=5,
                humanities=1,
                detail="Lautrec... TODO S&Q now or get later?",
            ),
            RunTo(f"{new_londo_elevator} then back entrance of Blighttown"),
            Region("Blighttown"),
            Perform("Blighttown drop"),
            Kill(
                "Blowdart Sniper",
                souls=600,
                detail="run off ledge and plunging attack",
            ),
            Receive("Purple Moss", detail="Blowdart Sniper"),
            Heal("using Estus Flask", detail="on waterwheel"),
            FallDamage(
                "waterwheel onto scaffold then scaffold to ground",
                detail="RTSR setup, swamp poison finishes the job",
            ),
            UseMenu(
                "Purple Moss", detail="once in RTSR range and out of swamp"
            ),
            Kill("Quelaag", souls=20000),
            Receive("Soul of Quelaag", souls=8000, detail="Quelaag"),
            Receive(Item.TWIN_HUMANITIES, humanities=2, detail="Quelaag"),
            Activate("Second bell"),
            Receive(Item.BONE, detail="Second bell"),
            Use(Item.BONE),
        )


class FirelinkToSensFortress(Segment):
    def __init__(self):
        super().__init__(
            Region("Firelink Shrine"),
            RunTo(parish_elevator),
            UseMenu("Soul of Quelaag", detail=parish_elevator),
            Region("Undead Parish"),
            BonfireSit("Undead Parish"),
            Region("Sen's Fortress"),
            RunTo("room before 2nd boulder"),
            WaitFor("boulder to pass", detail="hitting enemy in room 5 times"),
            RunTo("top of ramp", detail="must go IMMEDIATELY after boulder"),
            BonfireSit("Sen's Fortress"),
        )


class SensFortressToDarkmoonTomb(Segment):
    def __init__(self):
        super().__init__(
            Region("Sen's Fortress"),
            RunTo(
                "hole at dead end below bonfire and to the right",
                detail="fall down it",
            ),
            Loot("Slumbering Dragoncrest Ring"),
            Use(Item.BONE),
            FallDamage("off right side of bridge, twice", detail="RTSR setup"),
            Kill(
                "Undead Knight Archer",
                souls=600,
                detail="just because he blocks the doorway",
            ),
            Kill(
                "Iron Golem",
                souls=40000,
                detail="try to stagger and knock him off",
            ),
            Receive("Core of an Iron Golem", souls=12000, detail="Iron Golem"),
            Receive(Item.HUMANITY, humanities=1, detail="Iron Golem"),
            Region("Anor Londo"),
            BonfireSit(
                "Anor Londo", detail="safety for rafters", optional=True
            ),
            RunTo("elevator"),
            UseMenu("Core of an Iron Golem", detail="elevator"),
            Activate("Bridge lever (2x)"),
            Equip(
                "Slumbering Dragoncrest Ring",
                slot="Ring 1",
                detail="while pushing bridge lever",
            ),
            BonfireSit("Darkmoon Tomb"),
            Activate("Bridge lever"),
        )


class DarkmoonTombToGiantBlacksmith(Segment):
    def __init__(self):
        super().__init__(
            Region("Anor Londo"),
            Activate("Bridge lever"),
            RunTo("sniper ledge"),
            Kill(
                "Silver Knight",
                souls=1300,
                detail="bait melee then run to make him fall",
            ),
            BonfireSit("Post-Sniper Bonfire"),
            RunTo("Giant Blacksmith"),
        )


# TODO:
# - 1 humanity from o&s
# - 1 humanity from pinwheel
# - 4 humanity from killing patches


class SL1MeleeOnlyGlitchless(Segment):
    def __init__(self):
        super().__init__()
        for segment in [
            InitialState(),
            PyromancerInitialState(),
            StartOfGame(),
            AsylumCellToFirelink(),
            FirelinkLoot(),
            FirelinkToReinforcedClub(),
            FirelinkToAndre(),
            NormalUpgradeWeaponPlus5(),
            AndreToGargoyles(),
            FirelinkToQuelaag(),
            FirelinkToSensFortress(),
            SensFortressToDarkmoonTomb(),
            DarkmoonTombToGiantBlacksmith(),
        ]:
            self += segment
