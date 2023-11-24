from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum, unique

from .action import (
    Activate,
    AutoBonfire,
    AutoEquip,
    AutoKill,
    BonfireSit,
    Buy,
    Equip,
    FallDamage,
    Heal,
    Item,
    Jump,
    Kill,
    Loot,
    Perform,
    Receive,
    Region,
    RunTo,
    Talk,
    UnEquip,
    UpgradeCost,
    Use,
    UseMenu,
    WaitFor,
)
from .segment import Conditional, Segment

new_londo_elevator = "elevator to New Londo Ruins"
basin_elevator = "elevator to Darkroot Basin"
parish_elevator = "elevator to Undead Parish"
andre = "Andre of Astora"
O_and_S = "Dragon Slayer Ornstein & Executioner Smough"
sif = "Sif, the Great Grey Wolf"


@dataclass
class RouteOptions:
    early_weapon: str
    initial_upgrade: int
    loot_firelink_humanity: bool
    loot_firelink_elevator_soul: bool
    loot_firelink_bones: bool
    loot_firelink_graveyard: bool
    loot_new_londo_ruins_soul: bool
    loot_undead_parish_fire_keeper_soul: bool
    kill_black_knight: bool
    # defaulted
    wait_for_slow_humanities: bool = False
    wait_for_four_kings_humanities: bool = False
    kill_oswald: bool = False
    bone_count_if_from_oswald: int = 5
    kill_smough_first: bool = False

    def __post_init__(self) -> None:
        if self.initial_upgrade < 0 or self.initial_upgrade > 5:
            raise RuntimeError(
                f"initial_upgrade must be in range [0,5]"
                f" but is {self.initial_upgrade}"
            )


@unique
class Route(Enum):
    REINFORCED_CLUB = RouteOptions(
        early_weapon="Reinforced Club",
        initial_upgrade=5,
        loot_firelink_humanity=False,
        loot_firelink_elevator_soul=True,
        loot_firelink_bones=True,
        loot_firelink_graveyard=True,
        loot_new_londo_ruins_soul=True,
        loot_undead_parish_fire_keeper_soul=True,
        kill_black_knight=True,
    )
    BATTLE_AXE_PLUS3 = RouteOptions(
        early_weapon="Battle Axe",
        initial_upgrade=3,
        loot_firelink_humanity=False,
        loot_firelink_elevator_soul=False,
        loot_firelink_bones=False,
        loot_firelink_graveyard=False,
        loot_new_londo_ruins_soul=True,
        loot_undead_parish_fire_keeper_soul=True,
        kill_black_knight=True,
        kill_oswald=True,
    )
    BATTLE_AXE_PLUS4 = RouteOptions(
        early_weapon="Battle Axe",
        initial_upgrade=4,
        loot_firelink_humanity=False,
        loot_firelink_elevator_soul=False,
        loot_firelink_bones=False,
        loot_firelink_graveyard=False,
        loot_new_londo_ruins_soul=True,
        loot_undead_parish_fire_keeper_soul=True,
        kill_black_knight=True,
    )
    BATTLE_AXE_PLUS4_NO_BLACK_KNIGHT = RouteOptions(
        early_weapon="Battle Axe",
        initial_upgrade=4,
        loot_firelink_humanity=False,
        loot_firelink_elevator_soul=False,
        loot_firelink_bones=True,
        loot_firelink_graveyard=True,
        loot_new_londo_ruins_soul=True,
        loot_undead_parish_fire_keeper_soul=True,
        kill_black_knight=False,
    )

    @property  # not needed, but reads better in the code
    def options(self) -> RouteOptions:
        return self.value

    @property
    def uses_reinforced_club(self) -> bool:
        return self.options.early_weapon == "Reinforced Club"

    @property
    def uses_battle_axe(self) -> bool:
        return self.options.early_weapon == "Battle Axe"


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


class SL1StartToAfterGargoylesInFirelink(Segment):
    def __init__(self, route: Route, skip_firelink_loot: bool = False):
        ladder = "climbing ladder to RTSR"
        SHARDS_PER_LEVEL = [1, 1, 2, 2, 3]
        options = route.options
        pre_gargoyle_shards = sum(
            SHARDS_PER_LEVEL[0 : options.initial_upgrade]
        )
        post_gargoyle_shards = sum(SHARDS_PER_LEVEL[options.initial_upgrade :])
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
                        condition=options.loot_firelink_humanity,
                    ),
                    Loot(
                        "Soul of a Lost Undead",
                        souls=200,
                        detail="upper elevator",
                        condition=options.loot_firelink_elevator_soul,
                    ),
                    Jump(
                        "off ledge to hidden chests",
                        condition=options.loot_firelink_bones,
                    ),
                    Loot(
                        Item.BONE,
                        count=6,
                        detail="hidden chest",
                        condition=options.loot_firelink_bones,
                    ),
                    Equip(
                        Item.BONE,
                        "Item 5",
                        detail="immediately",
                        condition=options.loot_firelink_bones,
                    ),
                    Loot(
                        "Large Soul of a Lost Undead",
                        souls=400,
                        detail="middle of graveyard",
                        condition=options.loot_firelink_graveyard,
                    ),
                    Loot(
                        "Large Soul of a Lost Undead",
                        souls=400,
                        detail="start of graveyard",
                        condition=options.loot_firelink_graveyard,
                    ),
                    Use(Item.BONE, condition=options.loot_firelink_graveyard),
                ),
                Conditional(
                    route.uses_reinforced_club,
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
                        allow_partial=True,
                    ),
                    UseMenu(
                        "Soul of a Lost Undead",
                        detail=new_londo_elevator,
                        allow_partial=True,
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
                        condition=route.uses_reinforced_club,
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
                        condition=options.kill_black_knight,
                    ),
                    RunTo(
                        "Undead Parish",
                        detail=(
                            ""
                            if options.kill_black_knight
                            else "no need to kill Black Knight"
                        ),
                    ),
                    Region("Undead Parish"),
                    Buy(
                        "Battle Axe",
                        souls=1000,
                        detail=andre,
                        condition=route.uses_battle_axe,
                    ),
                ),
                Conditional(
                    options.initial_upgrade > 0,
                    Segment(
                        Buy(
                            Item.TITANITE_SHARD,
                            count=pre_gargoyle_shards,
                            souls=800,
                            detail=andre,
                        ),
                        UpgradeCost(
                            (
                                f"{options.early_weapon}"
                                f" +0-{options.initial_upgrade}"
                            ),
                            souls=200 * options.initial_upgrade,
                            items=Counter(
                                {Item.TITANITE_SHARD: pre_gargoyle_shards}
                            ),
                            detail=andre,
                        ),
                        Equip(
                            "Battle Axe",
                            "Right Hand",
                            detail=andre,
                            condition=route.uses_battle_axe,
                        ),
                    ),
                ),
                Segment(
                    BonfireSit(
                        "Undead Parish",
                        detail="to upgrade to +5 after Bell Gargoyles",
                        condition=(options.initial_upgrade < 5),
                    ),
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
                        condition=options.loot_undead_parish_fire_keeper_soul,
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
                    RunTo(
                        "Oswald of Carim",
                        detail="RTSR setup: heal, fall down both ladders",
                        condition=(
                            options.kill_oswald
                            or not options.loot_firelink_bones
                        ),
                    ),
                    Buy(
                        Item.BONE,
                        count=options.bone_count_if_from_oswald,
                        souls=500,
                        detail="Oswald of Carim",
                        condition=not options.loot_firelink_bones,
                    ),
                    Kill(
                        "Oswald of Carim",
                        souls=2000,
                        detail="can buy bones here",
                        condition=options.kill_oswald,
                    ),
                    Loot(
                        Item.TWIN_HUMANITIES,
                        count=2,
                        humanities=2,
                        detail="Oswald of Carim",
                        condition=options.kill_oswald,
                    ),
                    Equip(
                        Item.BONE,
                        "Item 5",
                        detail="immediately",
                        condition=not options.loot_firelink_bones,
                    ),
                    Use(Item.BONE),
                ),
                Conditional(
                    options.initial_upgrade < 5,
                    Segment(
                        Buy(
                            Item.TITANITE_SHARD,
                            count=post_gargoyle_shards,
                            souls=800,
                            detail=andre,
                        ),
                        UpgradeCost(
                            (
                                f"{options.early_weapon}"
                                f" +{options.initial_upgrade}-5"
                            ),
                            souls=200 * (5 - options.initial_upgrade),
                            items=Counter(
                                {Item.TITANITE_SHARD: post_gargoyle_shards}
                            ),
                            detail=andre,
                        ),
                        RunTo(parish_elevator),
                        Region("Firelink Shrine"),
                    ),
                ),
            ]
        )


class SL1MeleeOnlyGlitchless(Segment):
    def __init__(self, route: Route):
        options = route.options
        super().__init__(
            name=f"SL1 Melee Only Glitchless ({options.early_weapon})",
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
                (
                    "Black Knight with Hand Axe +0 with RTSR"
                    " takes 3 ripostes + 1 hit."
                    # 10 + 179
                ),
            ],
        )

        self.extend(
            [
                SL1StartToAfterGargoylesInFirelink(
                    route=Route.REINFORCED_CLUB
                    # route=Route.BATTLE_AXE_PLUS4
                    # route=Route.BATTLE_AXE_PLUS4_NO_BLACK_KNIGHT
                    # route=Route.BATTLE_AXE_PLUS3
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
                Segment(
                    Region("TODO"),
                    Kill(O_and_S, souls=50000),
                    Receive(
                        "Soul of Smough",
                        souls=12000,
                        detail=O_and_S,
                        condition=not options.kill_smough_first,
                    ),
                    Receive(
                        "Soul of Ornstein",
                        souls=12000,
                        detail=O_and_S,
                        condition=options.kill_smough_first,
                    ),
                    # Loot(
                    #    "Leo Ring",
                    #    detail=O_and_S,
                    #    condition=options.kill_smough_first,
                    # ),
                    Receive(Item.HUMANITY, humanities=1, detail=O_and_S),
                    Kill("Pinwheel", souls=15000),
                    Receive("Rite of Kindling", detail="Pinwheel"),
                    Receive(Item.HUMANITY, humanities=1, detail="Pinwheel"),
                    Receive(Item.BONE, detail="Pinwheel"),
                    Kill("Gravelord Nito", souls=60000),
                    Receive("Lord Soul", detail="Gravelord Nito"),
                    Receive(
                        Item.HUMANITY,
                        humanities=1,
                        detail="(Gravelord Nito) slow to receive it",
                        condition=options.wait_for_slow_humanities,
                    ),
                    Kill(sif, souls=40000),
                    Receive("Covenant of Artorias", detail=sif),
                    Receive("Soul of Sif", souls=16000, detail=sif),
                    Receive(
                        Item.HUMANITY,
                        humanities=1,
                        detail=f"({sif}) slow to receive it",
                        condition=options.wait_for_slow_humanities,
                    ),
                    Receive(Item.BONE, detail=sif),
                    Kill("The Four Kings", souls=60000),
                    Receive(
                        "Bequeathed Lord Soul Shard", detail="The Four Kings"
                    ),
                    Receive(
                        Item.HUMANITY,
                        count=4,
                        humanities=1,
                        detail="(The Four Kings) slow to receive it",
                        condition=options.wait_for_four_kings_humanities,
                    ),
                    Kill(
                        "Darkmoon Knightess",
                        souls=1000,
                        detail="Anor Londo fire keeper",
                    ),
                    Loot("Fire Keeper Soul", detail="Darkmoon Knightess"),
                    Kill("Seath the Scaleless", souls=60000),
                    Receive(
                        "Bequeathed Lord Soul Shard",
                        detail="Seath the Scaleless",
                    ),
                    Receive(
                        Item.HUMANITY,
                        humanities=1,
                        optional=True,
                        detail="(Seath the Scaleless) slow to receive it",
                        condition=options.wait_for_slow_humanities,
                    ),
                    Kill("Patches", souls=2000, detail="Tomb of the Giants"),
                    Loot(
                        Item.HUMANITY, count=4, humanities=1, detail="Patches"
                    ),
                    Kill("Petrus of Thorolund", souls=1000),
                    Loot(
                        Item.HUMANITY,
                        count=2,
                        humanities=1,
                        detail="Petrus of Thorolund",
                    ),
                    Kill(andre, souls=1000),
                    Loot(Item.HUMANITY, count=3, humanities=1, detail=andre),
                    UseMenu(
                        "Fire Keeper Soul",
                        count=6,
                        allow_partial=True,
                        detail="use all that you have",
                    ),
                    UseMenu(
                        Item.HUMANITY,
                        count=30,
                        allow_partial=True,
                        detail="use all that you have",
                    ),
                    UseMenu(
                        Item.TWIN_HUMANITIES,
                        count=15,
                        allow_partial=True,
                        detail="use all that you have",
                    ),
                ),
            ]
        )


# TODO:
# - check timing for grabbing firelink souls
# - check killing petrus with upgrades
# - check killing patches with upgrades
# - check killing darkmoon knightess with upgrades
# - check killing oswald with upgrades
# - make multiple routes be output
