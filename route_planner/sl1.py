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
from .segment import Segment, conditional

rtsr_ladder = "climbing ladder to RTSR"
new_londo_elevator = "elevator to New Londo Ruins"
basin_elevator = "elevator to Darkroot Basin"
parish_elevator = "elevator to Undead Parish"
andre = "Andre of Astora"
petrus = "Petrus of Thorolund"
O_and_S = "Dragon Slayer Ornstein & Executioner Smough"
sif = "Sif, the Great Grey Wolf"
nito = "Gravelord Nito"
seath = "Seath the Scaleless"
four_kings = "The Four Kings"


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
    wait_for_four_kings_drops: bool
    # defaulted
    wait_for_sif_drops: bool = False
    wait_for_nito_drops: bool = False
    wait_for_seath_drops: bool = False
    kill_oswald: bool = False
    kill_andre: bool = False
    kill_petrus: bool = False
    kill_patches: bool = False
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
        loot_firelink_humanity=True,
        loot_firelink_elevator_soul=True,
        loot_firelink_bones=True,
        loot_firelink_graveyard=True,
        loot_new_londo_ruins_soul=True,
        loot_undead_parish_fire_keeper_soul=True,
        kill_black_knight=True,
        wait_for_four_kings_drops=True,
    )
    BATTLE_AXE_PLUS3 = RouteOptions(
        early_weapon="Battle Axe",
        initial_upgrade=3,
        loot_firelink_humanity=True,
        loot_firelink_elevator_soul=False,
        loot_firelink_bones=False,
        loot_firelink_graveyard=False,
        loot_new_londo_ruins_soul=False,
        loot_undead_parish_fire_keeper_soul=True,
        kill_black_knight=False,
        wait_for_four_kings_drops=True,
    )
    BATTLE_AXE_PLUS4 = RouteOptions(
        early_weapon="Battle Axe",
        initial_upgrade=4,
        loot_firelink_humanity=True,
        loot_firelink_elevator_soul=False,
        loot_firelink_bones=False,
        loot_firelink_graveyard=False,
        loot_new_londo_ruins_soul=False,
        loot_undead_parish_fire_keeper_soul=True,
        kill_black_knight=True,
        wait_for_four_kings_drops=True,
    )
    BATTLE_AXE_PLUS4_NO_BLACK_KNIGHT = RouteOptions(
        early_weapon="Battle Axe",
        initial_upgrade=4,
        loot_firelink_humanity=True,
        loot_firelink_elevator_soul=False,
        loot_firelink_bones=True,
        loot_firelink_graveyard=True,
        loot_new_londo_ruins_soul=True,
        loot_undead_parish_fire_keeper_soul=True,
        kill_black_knight=False,
        wait_for_four_kings_drops=True,
    )

    @property  # not needed, but reads better in the code
    def options(self) -> RouteOptions:
        return self.value

    @property
    def loots_firelink_at_start(self) -> bool:
        return (
            self.options.loot_firelink_elevator_soul
            or self.options.loot_firelink_bones
            or self.options.loot_firelink_graveyard
        )

    @property
    def uses_reinforced_club(self) -> bool:
        return self.options.early_weapon == "Reinforced Club"

    @property
    def uses_battle_axe(self) -> bool:
        return self.options.early_weapon == "Battle Axe"


@dataclass
class InitialState(Segment):
    def __post_init__(self):
        detail = "starting equipment"
        super().__post_init__()
        self.add_steps(
            Receive(Item.DARKSIGN, detail=detail),
            Receive("Straight Sword Hilt", detail=detail),
            AutoEquip("Straight Sword Hilt", "Right Hand", detail=detail),
        )


@dataclass
class PyromancerInitialState(Segment):
    def __post_init__(self):
        detail = "Pyromancer starting equipment"
        super().__post_init__()
        self.add_steps(
            Receive("Tattered Cloth Hood", detail=detail),
            Receive("Tattered Cloth Robe", detail=detail),
            Receive("Tattered Cloth Manchette", detail=detail),
            Receive("Heavy Boots", detail=detail),
            AutoEquip("Tattered Cloth Hood", "Head", detail=detail),
            AutoEquip("Tattered Cloth Robe", "Torso", detail=detail),
            AutoEquip("Tattered Cloth Manchette", "Arms", detail=detail),
            AutoEquip("Heavy Boots", "Legs", detail=detail),
        )


@dataclass
class StartOfGame(Segment):
    def __post_init__(self):
        super().__post_init__()
        self.add_steps(
            Region("Northern Undead Asylum"),
            AutoBonfire("Undead Asylum Dungeon Cell"),
        )


@dataclass
class AsylumCellToFirelink(Segment):
    def __post_init__(self):
        super().__post_init__()
        self.add_steps(
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


@dataclass
class FirelinkToQuelaag(Segment):
    def __post_init__(self):
        super().__post_init__()
        self.add_steps(
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


@dataclass(kw_only=True)
class FirelinkToSensFortress(Segment):
    route: Route

    def __post_init__(self):
        options = self.route.options
        super().__post_init__()
        self.add_steps(
            Region("Firelink Shrine"),
            Loot(
                Item.HUMANITY,
                count=3,
                humanities=1,
                detail=f"side of well, get on way to {parish_elevator}.",
                condition=(
                    options.loot_firelink_humanity
                    and not self.route.loots_firelink_at_start
                    and not self.route.uses_reinforced_club
                ),
                notes=[
                    (
                        "3 humanities at Firelink well looted on way to"
                        " elevator before Sens Fortress."
                    )
                ],
            ),
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


@dataclass
class SensFortressToDarkmoonTomb(Segment):
    def __post_init__(self):
        super().__post_init__()
        self.add_steps(
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


@dataclass
class DarkmoonTombToGiantBlacksmith(Segment):
    def __post_init__(self):
        super().__post_init__()
        self.add_steps(
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


@dataclass
class GetBlacksmithGiantHammerAndUpgradeMaterials(Segment):
    def __post_init__(self):
        super().__post_init__()
        self.add_steps(
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


@dataclass
class EquipBlacksmithGiantHammerAndDarksign(Segment):
    def __post_init__(self):
        super().__post_init__()
        self.add_steps(
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


@dataclass(kw_only=True)
class SL1StartToAfterGargoylesInFirelink(Segment):
    route: Route

    def __post_init__(self):
        SHARDS_PER_LEVEL = [1, 1, 2, 2, 3]
        options = self.route.options
        early_weapon_shards = sum(
            SHARDS_PER_LEVEL[0 : options.initial_upgrade]
        )

        super().__post_init__()
        self.add_steps(
            InitialState(),
            PyromancerInitialState(),
            StartOfGame(),
            AsylumCellToFirelink(),
            Region("Firelink Shrine"),
            conditional(
                not self.route.loots_firelink_at_start,
                notes=[
                    "Firelink IS NOT looted at start;"
                    f" goes straight to {andre}."
                ],
            ),
            conditional(
                self.route.loots_firelink_at_start,
                Loot(
                    Item.HUMANITY,
                    count=3,
                    humanities=1,
                    detail="side of well, get during Firelink loot route.",
                    condition=(
                        options.loot_firelink_humanity
                        and not self.route.uses_reinforced_club
                    ),
                    notes=[
                        "3 humanities at Firelink well looted immediately."
                    ],
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
                notes=["Firelink is looted upon arrival."],
            ),
            conditional(
                self.route.uses_reinforced_club,
                Region("Firelink Shrine"),
                Loot(
                    Item.HUMANITY,
                    count=3,
                    humanities=1,
                    detail=(
                        "side of well, get on way" " to get Reinforced Club"
                    ),
                    condition=options.loot_firelink_humanity,
                ),
                RunTo("Undead Burg"),
                Region("Undead Burg"),
                Buy("Reinforced Club", souls=350, detail="Undead Merchant"),
                Buy(
                    "Firebomb",
                    souls=50,
                    count=3,
                    detail="(Undead Merchant) if using Tohki Bombs",
                    optional=True,
                ),
                Use(Item.BONE),
            ),
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
                condition=options.loot_new_londo_ruins_soul,
            ),
            RunTo("Master Key door to Valley of the Drakes"),
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
            Equip(
                "Reinforced Club",
                "Right Hand",
                detail=rtsr_ladder,
                condition=self.route.uses_reinforced_club,
            ),
            Equip(
                "Soul of a Nameless Soldier",
                "Item 2",
                detail=rtsr_ladder,
                condition=options.loot_new_londo_ruins_soul,
            ),
            Equip(
                "Large Soul of a Nameless Soldier",
                "Item 3",
                detail=rtsr_ladder,
            ),
            Equip("Soul of a Proud Knight", "Item 4", detail=rtsr_ladder),
            Loot("Red Tearstone Ring"),
            FallDamage(
                "ledge by Red Tearstone Ring", detail="RTSR setup (2/3)"
            ),
            RunTo(basin_elevator),
            Use("Large Soul of a Nameless Soldier", detail=basin_elevator),
            Use("Soul of a Proud Knight", detail=basin_elevator),
            Use(
                "Soul of a Nameless Soldier",
                detail=basin_elevator,
                condition=options.loot_new_londo_ruins_soul,
            ),
            Equip("Red Tearstone Ring", "Ring 2", detail=basin_elevator),
            Region("Darkroot Basin"),
            Loot("Grass Crest Shield"),
            Equip("Grass Crest Shield", "Left Hand", detail="immediately"),
            Kill(
                "Black Knight",
                souls=1800,
                detail="by Grass Crest Shield",
                condition=options.kill_black_knight,
                notes=["Black Knight in Darkroot Basin MUST be killed."],
            ),
            conditional(
                not options.kill_black_knight,
                notes=["Black Knight in Darkroot Basin DOES NOT need killed."],
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
                condition=self.route.uses_battle_axe,
            ),
            conditional(
                options.initial_upgrade > 0,
                Buy(
                    Item.TITANITE_SHARD,
                    count=early_weapon_shards,
                    souls=800,
                    detail=andre,
                ),
                UpgradeCost(
                    (
                        f"{options.early_weapon}"
                        f" +0-{options.initial_upgrade}"
                    ),
                    souls=200 * options.initial_upgrade,
                    items=Counter({Item.TITANITE_SHARD: early_weapon_shards}),
                    detail=andre,
                ),
                Equip(
                    "Battle Axe",
                    "Right Hand",
                    detail=andre,
                    condition=self.route.uses_battle_axe,
                ),
            ),
            Loot(
                "Fire Keeper Soul",
                humanities=5,
                detail="on altar behind Berenike Knight",
                condition=options.loot_undead_parish_fire_keeper_soul,
            ),
            Activate(
                "Elevator to Firelink Shrine",
                detail="run in, trigger it, run back out",
            ),
            Kill("Bell Gargoyles", souls=10000),
            Receive(
                Item.TWIN_HUMANITIES, humanities=2, detail="Bell Gargoyles"
            ),
            Activate("First bell"),
            RunTo(
                "Oswald of Carim",
                detail="TODO: RTSR setup: heal, fall down both ladders",
                condition=(
                    options.kill_oswald or not options.loot_firelink_bones
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
        )


@dataclass(kw_only=True)
class SL1MeleeOnlyGlitchless(Segment):
    route: Route

    def __post_init__(self):
        options = self.route.options
        super().__post_init__()
        if not self.name:
            self.name = f"SL1 Melee Only Glitchless ({self.route.name})"
        self.notes.extend(["TODO: fix RTSR setup for Gargoyles"])
        if self.route.uses_reinforced_club:
            self.notes.extend(
                [
                    "Quelaag dies in 11 heavy RTSR hits (jumping).",
                    "Iron Golem staggers in 3 weak RTSR hits and falls in 2.",
                ]
            )
        self.add_steps(
            SL1StartToAfterGargoylesInFirelink(route=self.route),
            FirelinkToQuelaag(),
            FirelinkToSensFortress(route=self.route),
            SensFortressToDarkmoonTomb(),
            DarkmoonTombToGiantBlacksmith(),
            GetBlacksmithGiantHammerAndUpgradeMaterials(),
            UpgradeCost(
                "Blacksmith Giant Hammer +0-5",
                souls=10000,
                items=Counter({Item.TWINKLING_TITANITE: 10}),
                detail="(Bonfire) Blacksmith Giant Hammer +0-5",
            ),
            EquipBlacksmithGiantHammerAndDarksign(),
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
            Kill(nito, souls=60000),
            Receive("Lord Soul", detail=nito),
            conditional(
                not options.wait_for_nito_drops,
                notes=[f"1 slow {Item.HUMANITY} skipped from {nito}."],
            ),
            conditional(
                options.wait_for_nito_drops,
                Receive(
                    Item.HUMANITY,
                    humanities=1,
                    detail=f"{nito} (slow to receive it)",
                ),
                notes=[f"wait for 1 slow {Item.HUMANITY} from {nito}."],
            ),
            Kill(sif, souls=40000),
            Receive("Covenant of Artorias", detail=sif),
            Receive("Soul of Sif", souls=16000, detail=sif),
            conditional(
                not options.wait_for_sif_drops,
                notes=[
                    f"1 slow {Item.HUMANITY} and {Item.BONE}"
                    f" skipped from {sif}."
                ],
            ),
            conditional(
                options.wait_for_sif_drops,
                Receive(
                    Item.HUMANITY,
                    humanities=1,
                    detail=f"{sif} (slow to receive it)",
                ),
                Receive(Item.BONE, detail=f"{sif} (slow to receive it)"),
                notes=[f"wait for 1 slow {Item.HUMANITY} from {sif}."],
            ),
            Kill(four_kings, souls=60000),
            Receive("Bequeathed Lord Soul Shard", detail=four_kings),
            conditional(
                not options.wait_for_four_kings_drops,
                notes=[
                    f"4 slow {Item.HUMANITY}" " skipped from {four_kings}."
                ],
            ),
            conditional(
                options.wait_for_four_kings_drops,
                Receive(
                    Item.HUMANITY,
                    count=4,
                    humanities=1,
                    detail=f"{four_kings} (slow to receive it)",
                ),
                notes=[
                    f"wait for 4 slow {Item.HUMANITY}" f" from {four_kings}."
                ],
            ),
            Kill(
                "Darkmoon Knightess",
                souls=1000,
                detail="Anor Londo fire keeper",
            ),
            Loot("Fire Keeper Soul", detail="Darkmoon Knightess"),
            Kill(seath, souls=60000),
            Receive("Bequeathed Lord Soul Shard", detail=seath),
            conditional(
                not options.wait_for_seath_drops,
                notes=[f"1 slow {Item.HUMANITY} skipped from {seath}."],
            ),
            conditional(
                options.wait_for_seath_drops,
                Receive(
                    Item.HUMANITY,
                    humanities=1,
                    detail=f"{seath} (slow to receive it)",
                ),
                notes=[f"wait for 1 slow humanity from {seath}."],
            ),
            Kill(
                "Patches",
                souls=2000,
                detail="Tomb of the Giants",
                condition=options.kill_patches,
            ),
            Loot(
                Item.HUMANITY,
                count=4,
                humanities=1,
                detail="Patches",
                condition=options.kill_patches,
            ),
            Kill(petrus, souls=1000, condition=options.kill_petrus),
            Loot(
                Item.HUMANITY,
                count=2,
                humanities=1,
                detail=petrus,
                condition=options.kill_petrus,
            ),
            Kill(andre, souls=1000, condition=options.kill_andre),
            Loot(
                Item.HUMANITY,
                count=3,
                humanities=1,
                detail=andre,
                condition=options.kill_andre,
            ),
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
        )


# MISPLACED NOTES:
# "Getting the Reinforced Club takes just under a minute.",
# (
#    "You can't run back to Andre to finish upgrading unless"
#    " you sit in Undead Parish and lose RTSR range.  Elevator"
#    " RTSR strat takes 50-55 seconds, and running to Andre to"
#    " upgrade takes 20-30 seconds."
# ),
# (
#    "The Battle Axe route would mean using the Hand Axe"
#    " against the Black Knight, boss fights would be longer"
#    " and the Iron Golem in particular would be harder."
# ),
# (
#    "Black Knight with Hand Axe +0 with RTSR"
#    " takes 3 ripostes + 1 hit. (10+179)"
# ),


# TODO:
# - check if the firelink elevator soul is best for Reinforced Club route
#   or if perhaps the one on the way to get the weapon is better.
# - check timing for grabbing firelink humanities
# - determine when to loot Lautrec, or how to replace him (quitoutless)
# - add ability to estimate time for a segment
# - fix RTSR setup for gargoyles
# - add variable to configure number of painting guardians to count on dying?

# Data to get:
# - Firelink
#   - seconds to loot Firelink fully and bone
#   - seconds to loot Firelink fully and bone (without elevator soul)
#   - seconds to get Reinforced Club (~1 minute)
# - Black Knight
#   - seconds to kill Black Knight with +0 Hand Axe and RTSR
#   - seconds to kill Black Knight with +0 Reinforced Club and RTSR
#   - seconds to kill Black Knight with unintended ledge fall
#   - damage/hits with +0 Hand Axe and Reinforced Club
# - Darkroot Basin
#   - seconds to get soul item toward secret bonfire and run back (slow)
#   - seconds from Reinforced Club through Havel's door to Grass Crest Shield
#   - seconds from Grass Crest Shield backwards to RTSR
# - Undead Parish
#   - seconds to get RTSR if sat at Andre/darkroot basin
# - Bell Gargoyles/Quelaag/Iron Golem stagger + fall/Giant Blacksmith
#   - damage/hits with +3 and +4 Battle Axe and +5 Reinforced Club
