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
    UpgradeCost,
    Use,
    UseMenu,
    WaitFor,
)
from .route import Conditional, Route, Segment
from collections import Counter
from enum import auto, StrEnum

new_londo_elevator = "elevator to New Londo Ruins"
basin_elevator = "elevator to Darkroot Basin"
parish_elevator = "elevator to Undead Parish"


class EarlyWeapon(StrEnum):
    REINFORCED_CLUB = "Reinforced Club"
    BATTLE_AXE = "Battle Axe"

    @property
    def is_reinforced_club(self) -> bool:
        return self == EarlyWeapon.REINFORCED_CLUB

    @property
    def is_battle_axe(self) -> bool:
        return self == EarlyWeapon.BATTLE_AXE


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
            Receive(Item.HUMANITY, humanities=1, detail="Asylum Demon"),
            Receive("Big Pilgrim's Key", detail="Asylum Demon"),
            Activate("Big Pilgrim's Key Door", detail="Asylum Demon"),
            Activate("Ledge warp trigger to Firelink Shrine"),
            Region("Firelink Shrine"),
            AutoBonfire("Firelink Shrine"),
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


class GetBlacksmithGiantHammerAndUpgradeMaterials(Segment):
    def __init__(self):
        super().__init__(
            Region("Anor Londo"),
            Buy("Weapon Smithbox", souls=2000, detail="Giant Blacksmith"),
            Buy(
                Item.TWINKLING_TITANITE,
                count=10,
                souls=8000,
                detail="Giant Blacksmith",
            ),
            Kill("Giant Blacksmith", souls=3000),
            Loot("Blacksmith Giant Hammer", detail="Giant Blacksmith"),
            Use(Item.BONE),
        )


class EquipBlacksmithGiantHammerAndDarksign(Segment):
    def __init__(self):
        super().__init__(
            Equip(
                "Blacksmith Giant Hammer",
                "Right Hand",
                detail="could wait until O&S fog gate",
            ),
            Equip(
                Item.DARKSIGN,
                "Item 5",
                detail="no need for bones anymore",
                expected_to_replace=Item.BONE,
            ),
        )


# TODO:
# - 1 humanity from o&s
# - 1 humanity from pinwheel
# - 4 humanity from killing patches


class SL1StartToAfterGargoylesInFirelink(Segment):
    def __init__(self, early_weapon: EarlyWeapon):
        ladder = "climbing ladder to RTSR"
        super().__init__()

        self.extend(
            [
                InitialState(),
                PyromancerInitialState(),
                StartOfGame(),
                AsylumCellToFirelink(),
                Segment(
                    Region("Firelink Shrine"),
                    Loot(
                        Item.HUMANITY,
                        count=3,
                        humanities=1,
                        detail="side of well",
                    ),
                    Loot(
                        "Soul of a Lost Undead",
                        souls=200,
                        detail="upper elevator",
                        enabled=early_weapon.is_reinforced_club,
                    ),
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
                ),
                Conditional(
                    early_weapon.is_reinforced_club,
                    Segment(
                        Region("Firelink Shrine"),
                        RunTo("Undead Burg"),
                        Region("Undead Burg"),
                        Buy(
                            "Reinforced Club",
                            souls=350,
                            detail="Undead Merchant",
                        ),
                        Buy(
                            "Firebomb",
                            souls=50,
                            count=3,
                            detail="(Undead Merchant) if using Tohki Bombs",
                            optional=True,
                        ),
                        Use(Item.BONE),
                    ),
                ),
                Segment(
                    Region("Firelink Shrine"),
                    RunTo(new_londo_elevator),
                    UseMenu(
                        "Large Soul of a Lost Undead",
                        count=2,
                        detail=new_londo_elevator,
                    ),
                    UseMenu(
                        "Soul of a Lost Undead",
                        detail=new_londo_elevator,
                        enabled=early_weapon.is_reinforced_club,
                    ),
                    Region("New Londo Ruins"),
                    Loot(
                        "Soul of a Nameless Soldier",
                        souls=800,
                        detail=f"by bottom of {new_londo_elevator}",
                    ),
                    RunTo("Master Key door to Valley of the Drakes"),
                    Region("Valley of Drakes"),
                    Loot(
                        "Large Soul of a Nameless Soldier",
                        souls=1000,
                        detail="behind master key door",
                    ),
                    FallDamage(
                        "ledge above Undead Dragon", detail="RTSR setup (1/3)"
                    ),
                    Loot(
                        "Soul of a Proud Knight",
                        souls=2000,
                        detail="last item by Undead Dragon",
                    ),
                    Equip(
                        "Reinforced Club",
                        "Right Hand",
                        detail=ladder,
                        enabled=early_weapon.is_reinforced_club,
                    ),
                    Equip(
                        "Soul of a Nameless Soldier", "Item 2", detail=ladder
                    ),
                    Equip(
                        "Large Soul of a Nameless Soldier",
                        "Item 3",
                        detail=ladder,
                    ),
                    Equip("Soul of a Proud Knight", "Item 4", detail=ladder),
                    Loot("Red Tearstone Ring"),
                    FallDamage(
                        "ledge by Red Tearstone Ring",
                        detail="RTSR setup (2/3)",
                    ),
                    RunTo(basin_elevator),
                    Use(
                        "Large Soul of a Nameless Soldier",
                        detail=basin_elevator,
                    ),
                    Use("Soul of a Proud Knight", detail=basin_elevator),
                    Use("Soul of a Nameless Soldier", detail=basin_elevator),
                    Equip(
                        "Red Tearstone Ring", "Ring 2", detail=basin_elevator
                    ),
                    Region("Darkroot Basin"),
                    Loot("Grass Crest Shield"),
                    Equip(
                        "Grass Crest Shield", "Left Hand", detail="immediately"
                    ),
                    Kill(
                        "Black Knight",
                        souls=1800,
                        detail="by Grass Crest Shield",
                        enabled=early_weapon.is_reinforced_club,
                    ),
                    RunTo(
                        "Undead Parish",
                        detail=(
                            ""
                            if early_weapon.is_reinforced_club
                            else "no need to kill Black Knight"
                        ),
                    ),
                    Region("Undead Parish"),
                ),
                Conditional(
                    early_weapon.is_battle_axe,
                    Segment(
                        Buy("Battle Axe", souls=1000, detail="Andre"),
                        Buy(
                            Item.TITANITE_SHARD,
                            count=6,
                            souls=800,
                            detail="Andre",
                        ),
                        UpgradeCost(
                            "Normal Weapon +0-4",
                            souls=800,
                            items=Counter({Item.TITANITE_SHARD: 6}),
                            detail="(Andre) Battle Axe +0-4",
                        ),
                        Equip("Battle Axe", "Right Hand", detail="Andre"),
                        BonfireSit(
                            "Undead Parish",
                            detail="to upgrade to +5 after Bell Gargoyles",
                        ),
                    ),
                ),
                Conditional(
                    not early_weapon.is_battle_axe,
                    Segment(
                        Buy(
                            Item.TITANITE_SHARD,
                            count=9,
                            souls=800,
                            detail="Andre",
                        ),
                        UpgradeCost(
                            "Normal Weapon +0-5",
                            souls=1000,
                            items=Counter({Item.TITANITE_SHARD: 9}),
                            detail=f"(Andre) {early_weapon} +0-5",
                        ),
                    ),
                ),
                Segment(
                    RunTo("gate area by Basement Key", detail="TODO: remove"),
                    FallDamage(
                        "right-side ledge above Basement key",
                        detail="RTSR setup (3/3)",
                        optional=True,  # so this is noticed
                    ),
                    Loot("Basement Key", detail="by gate lever"),
                    Loot(
                        "Fire Keeper Soul",
                        humanities=5,
                        detail="on altar behind Berenike Knight",
                    ),
                    Activate(
                        "Elevator to Firelink Shrine",
                        detail="TODO: remove? just run, don't roll",
                    ),
                    Kill("Bell Gargoyles", souls=10000),
                    Receive(
                        Item.TWIN_HUMANITIES,
                        humanities=2,
                        detail="Bell Gargoyles",
                    ),
                    Activate("First bell"),
                    Use(Item.BONE),
                ),
                Conditional(
                    early_weapon.is_battle_axe,
                    Segment(
                        Region("Undead Parish"),
                        Buy(
                            Item.TITANITE_SHARD,
                            count=3,
                            souls=800,
                            detail="Andre",
                        ),
                        UpgradeCost(
                            "Normal Weapon +4-5",
                            souls=200,
                            items=Counter({Item.TITANITE_SHARD: 3}),
                            detail="(Andre) Battle Axe +4-5",
                        ),
                        RunTo(parish_elevator),
                    ),
                ),
            ]
        )


class SL1MeleeOnlyGlitchless(Route):
    def __init__(self):
        super().__init__(
            "SL1 Melee Only Glitchless (Reinforced Club)",
            notes=[
                "Getting the Reinforced Club takes just under a minute.",
                (
                    "Quelaag dies in 11 heavy RTSR hits (jumping).  Battle Axe"
                    " takes 13 heavy RTSR hits (vertical) or 19 weak RTSR hits"
                    " (horizontal)."
                ),
                (
                    "Iron Golem staggers in 3 weak RTSR hits and falls in 2."
                    " Battle Axe takes 5 weak RTSR hits (horizontal) to"
                    " stagger and falls in 3."
                ),
                (
                    "Because Battle Axe costs 1000 souls, upgrades are 500"
                    " souls short of getting to +5, meaning running back to"
                    " Andre for +4 to +5.  With the Reinforced Club, you even"
                    " have 150 souls left over for Tohki bombs (optional)."
                ),
                (
                    "There's 200 souls across from snuggly, 200 around where"
                    " patches moves to firelink, and 200 on the ledge above"
                    " Frampt's position.  The Ent you run past drops 100."
                ),
                (
                    "If you get the soul across from Snuggly and kill the Ent,"
                    " you still need 200 more souls from somewhere and all of"
                    " this must take less than 1 minute to break even with the"
                    " Reinforced Club route."
                ),
                (
                    "The Battle Axe route would mean using the Hand Axe"
                    " against the Black Knight."
                ),
                (
                    "Running back to Andre and upgrading again takes around 20"
                    " seconds if you bone back."
                ),
                (
                    "Conclusion: Battle Axe means longer fights and 20 seconds"
                    " to upgrade again."
                ),
            ],
        )
        self.extend(
            [
                SL1StartToAfterGargoylesInFirelink(
                    early_weapon=EarlyWeapon.REINFORCED_CLUB
                    # early_weapon=EarlyWeapon.BATTLE_AXE
                ),
                FirelinkToQuelaag(),
                FirelinkToSensFortress(),
                SensFortressToDarkmoonTomb(),
                DarkmoonTombToGiantBlacksmith(),
                GetBlacksmithGiantHammerAndUpgradeMaterials(),
                Segment(
                    UpgradeCost(
                        "Unique Weapon to +5",
                        souls=10000,
                        items=Counter({Item.TWINKLING_TITANITE: 10}),
                        detail="(Bonfire) Blacksmith Giant Hammer +0-5",
                    )
                ),
                EquipBlacksmithGiantHammerAndDarksign(),
            ]
        )
