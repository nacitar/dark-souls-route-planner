from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, unique

from ..action import (
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
    TalkTo,
    UnEquip,
    UpgradeCost,
    Use,
    UseMenu,
    WaitFor,
    WarpTo,
)
from ..route import DamageTable, Enemy, HitType, Route, Segment, conditional
from ..sl1 import SL1_HIT_LOOKUP

rtsr_ladder = "climbing ladder to RTSR"
new_londo_elevator = "elevator to New Londo Ruins"
basin_elevator = "elevator to Darkroot Basin"
parish_elevator = "elevator to Undead Parish"
andre = "Andre of Astora"
petrus = "Petrus of Thorolund"
oswald = "Oswald of Carim"
O_and_S = "Dragon Slayer Ornstein & Executioner Smough"
sif = "Sif, the Great Grey Wolf"
nito = "Gravelord Nito"
seath = "Seath the Scaleless"
gwyndolin = "Dark Sun Gwyndolin"
four_kings = "The Four Kings"
priscilla = "Crossbreed Priscilla"
slumbering = "Slumbering Dragoncrest Ring"

HUMANOID_HIT_TYPES = list(HitType)
STANDARD_HIT_TYPES = [
    hit_type
    for hit_type in HitType
    if hit_type.name.split("_", 1)[0] not in ["BACKSTAB", "RIPOSTE"]
]
HUMANOID_HIT_TYPES_2H = [
    hit_type
    for hit_type in HUMANOID_HIT_TYPES
    if not hit_type.name.endswith("_1H")
]
STANDARD_HIT_TYPES_2H = [
    hit_type
    for hit_type in STANDARD_HIT_TYPES
    if not hit_type.name.endswith("_1H")
]

HUMANOID_ENEMIES_WITHOUT_UPGRADES = [Enemy.BLACK_KNIGHT_DARKROOT_BASIN]
ENEMIES_WITH_UPGRADES = [
    Enemy.BELL_GARGOYLES,
    Enemy.QUELAAG,
    Enemy.IRON_GOLEM,
    Enemy.GIANT_BLACKSMITH,
]
HUMANOID_ENEMIES_WITH_UPGRADES = [Enemy.OSWALD, Enemy.PETRUS, Enemy.LAUTREC]
ENEMIES_MAYBE_WITH_FINAL_WEAPON = [Enemy.MIMIC_OCCULT_CLUB]
HUMANOID_ENEMIES_MAYBE_WITH_FINAL_WEAPON = [Enemy.DARKMOON_KNIGHTESS]


@dataclass(kw_only=True)
class FirelinkOptions:
    loot_well_humanity: bool = False
    loot_elevator_soul: bool = False
    loot_homeward_bones: bool = False
    loot_graveyard_souls: bool = False


@dataclass(kw_only=True)
class NewLondoRuinsOptions:
    loot_elevator_soul: bool = False


@dataclass(kw_only=True)
class DarkrootBasinOptions:
    kill_black_knight: bool = False


@dataclass(kw_only=True)
class UndeadParishOptions:
    loot_fire_keeper_soul: bool = False


@dataclass(kw_only=True)
class UndeadAsylumOptions:
    trade_for_ring_of_fog: bool = False


@dataclass(kw_only=True)
class NpcOptions:
    kill_darkmoon_knightess: bool = False
    kill_oswald: bool = False
    kill_andre: bool = False
    kill_petrus: bool = False
    kill_patches: bool = False


@dataclass(kw_only=True)
class BossOptions:
    wait_for_four_kings_drops: bool = False
    wait_for_sif_drops: bool = False
    wait_for_nito_drops: bool = False
    wait_for_seath_drops: bool = False
    kill_smough_first: bool = False
    kill_stray_demon: bool = True


@dataclass(kw_only=True)
class RingOptions:
    ring_of_fog: bool = False
    slumbering_dragoncrest_ring: bool = False


@dataclass(kw_only=True)
class Options:
    display_name: str
    early_weapon: str
    initial_upgrade: int
    firelink: FirelinkOptions
    new_londo_ruins: NewLondoRuinsOptions
    darkroot_basin: DarkrootBasinOptions
    undead_parish: UndeadParishOptions
    undead_asylum: UndeadAsylumOptions
    boss: BossOptions
    npc: NpcOptions
    ring: RingOptions
    all_bosses: bool = False
    bone_count_if_from_oswald: int = 5
    notes: list[str] = field(default_factory=list)
    damage_tables: list[DamageTable] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.initial_upgrade < 0 or self.initial_upgrade > 5:
            raise RuntimeError(
                f"initial_upgrade must be in range [0,5]"
                f" but is {self.initial_upgrade}"
            )

    @property
    def loots_firelink_at_start(self) -> bool:
        return (
            self.firelink.loot_elevator_soul
            or self.firelink.loot_homeward_bones
            or self.firelink.loot_graveyard_souls
        )

    @property
    def uses_reinforced_club(self) -> bool:
        return self.early_weapon == "Reinforced Club"

    @property
    def uses_battle_axe(self) -> bool:
        return self.early_weapon == "Battle Axe"

    @property
    def revisits_undead_asylum(self) -> bool:
        return (
            self.boss.kill_stray_demon
            or self.undead_asylum.trade_for_ring_of_fog
        )


@unique
class Variation(Enum):
    REINFORCED_CLUB = Options(
        display_name="Reinforced Club +5",
        early_weapon="Reinforced Club",
        initial_upgrade=5,
        firelink=FirelinkOptions(
            loot_well_humanity=True,
            loot_elevator_soul=True,
            loot_homeward_bones=True,
            loot_graveyard_souls=True,
        ),
        new_londo_ruins=NewLondoRuinsOptions(loot_elevator_soul=True),
        darkroot_basin=DarkrootBasinOptions(kill_black_knight=True),
        undead_parish=UndeadParishOptions(loot_fire_keeper_soul=True),
        undead_asylum=UndeadAsylumOptions(),
        boss=BossOptions(wait_for_four_kings_drops=True),
        npc=NpcOptions(kill_darkmoon_knightess=True),
        ring=RingOptions(),
        notes=[],
        damage_tables=[
            DamageTable(
                weapon="Reinforced Club +0",
                enemies=HUMANOID_ENEMIES_WITHOUT_UPGRADES,
                hit_types=HUMANOID_HIT_TYPES,
            ),
            DamageTable(
                weapon="Reinforced Club +5",
                enemies=(
                    ENEMIES_WITH_UPGRADES + ENEMIES_MAYBE_WITH_FINAL_WEAPON
                ),
                hit_types=STANDARD_HIT_TYPES,
            ),
            DamageTable(
                weapon="Reinforced Club +5",
                enemies=(
                    HUMANOID_ENEMIES_WITH_UPGRADES
                    + HUMANOID_ENEMIES_MAYBE_WITH_FINAL_WEAPON
                ),
                hit_types=HUMANOID_HIT_TYPES,
            ),
            DamageTable(
                weapon="Blacksmith Giant Hammer +5",
                enemies=ENEMIES_MAYBE_WITH_FINAL_WEAPON,
                hit_types=STANDARD_HIT_TYPES_2H,
            ),
            DamageTable(
                weapon="Blacksmith Giant Hammer +5",
                enemies=HUMANOID_ENEMIES_MAYBE_WITH_FINAL_WEAPON,
                hit_types=HUMANOID_HIT_TYPES_2H,
            ),
        ],
    )
    BATTLE_AXE_PLUS_4_OR_3 = Options(
        display_name="Battle Axe +4 or +3",
        early_weapon="Battle Axe",
        initial_upgrade=4,
        firelink=FirelinkOptions(loot_well_humanity=True),
        new_londo_ruins=NewLondoRuinsOptions(),
        darkroot_basin=DarkrootBasinOptions(kill_black_knight=True),
        undead_parish=UndeadParishOptions(loot_fire_keeper_soul=True),
        undead_asylum=UndeadAsylumOptions(),
        boss=BossOptions(wait_for_four_kings_drops=True),
        npc=NpcOptions(kill_darkmoon_knightess=True),
        ring=RingOptions(),
        notes=[],
        damage_tables=[
            DamageTable(
                weapon="Hand Axe +0",
                enemies=HUMANOID_ENEMIES_WITHOUT_UPGRADES,
                hit_types=HUMANOID_HIT_TYPES,
            ),
            DamageTable(
                weapon="Battle Axe +4",
                enemies=(
                    ENEMIES_WITH_UPGRADES + ENEMIES_MAYBE_WITH_FINAL_WEAPON
                ),
                hit_types=STANDARD_HIT_TYPES,
            ),
            DamageTable(
                weapon="Battle Axe +4",
                enemies=(
                    HUMANOID_ENEMIES_WITH_UPGRADES
                    + HUMANOID_ENEMIES_MAYBE_WITH_FINAL_WEAPON
                ),
                hit_types=HUMANOID_HIT_TYPES,
            ),
            DamageTable(
                weapon="Battle Axe +3",
                enemies=(
                    ENEMIES_WITH_UPGRADES + ENEMIES_MAYBE_WITH_FINAL_WEAPON
                ),
                hit_types=STANDARD_HIT_TYPES,
            ),
            DamageTable(
                weapon="Battle Axe +3",
                enemies=(
                    HUMANOID_ENEMIES_WITH_UPGRADES
                    + HUMANOID_ENEMIES_MAYBE_WITH_FINAL_WEAPON
                ),
                hit_types=HUMANOID_HIT_TYPES,
            ),
            DamageTable(
                weapon="Blacksmith Giant Hammer +5",
                enemies=ENEMIES_MAYBE_WITH_FINAL_WEAPON,
                hit_types=STANDARD_HIT_TYPES_2H,
            ),
            DamageTable(
                weapon="Blacksmith Giant Hammer +5",
                enemies=HUMANOID_ENEMIES_MAYBE_WITH_FINAL_WEAPON,
                hit_types=HUMANOID_HIT_TYPES_2H,
            ),
        ],
    )
    BATTLE_AXE_PLUS_4_SKIPPING_BLACK_KNIGHT = Options(
        display_name="Battle Axe +4 skipping Black Knight",
        early_weapon="Battle Axe",
        initial_upgrade=4,
        firelink=FirelinkOptions(
            loot_well_humanity=True,
            loot_homeward_bones=True,
            loot_graveyard_souls=True,
        ),
        new_londo_ruins=NewLondoRuinsOptions(loot_elevator_soul=True),
        darkroot_basin=DarkrootBasinOptions(),
        undead_parish=UndeadParishOptions(loot_fire_keeper_soul=True),
        undead_asylum=UndeadAsylumOptions(),
        boss=BossOptions(wait_for_four_kings_drops=True),
        npc=NpcOptions(kill_darkmoon_knightess=True),
        ring=RingOptions(),
        notes=[],
        damage_tables=[
            DamageTable(
                weapon="Hand Axe +0",
                enemies=HUMANOID_ENEMIES_WITHOUT_UPGRADES,
                hit_types=HUMANOID_HIT_TYPES,
            ),
            DamageTable(
                weapon="Battle Axe +4",
                enemies=(
                    ENEMIES_WITH_UPGRADES + ENEMIES_MAYBE_WITH_FINAL_WEAPON
                ),
                hit_types=STANDARD_HIT_TYPES,
            ),
            DamageTable(
                weapon="Battle Axe +4",
                enemies=(
                    HUMANOID_ENEMIES_WITH_UPGRADES
                    + HUMANOID_ENEMIES_MAYBE_WITH_FINAL_WEAPON
                ),
                hit_types=HUMANOID_HIT_TYPES,
            ),
            DamageTable(
                weapon="Blacksmith Giant Hammer +5",
                enemies=ENEMIES_MAYBE_WITH_FINAL_WEAPON,
                hit_types=STANDARD_HIT_TYPES_2H,
            ),
            DamageTable(
                weapon="Blacksmith Giant Hammer +5",
                enemies=HUMANOID_ENEMIES_MAYBE_WITH_FINAL_WEAPON,
                hit_types=HUMANOID_HIT_TYPES_2H,
            ),
        ],
    )

    @property  # not needed, but reads better in the code
    def options(self) -> Options:
        return self.value


@dataclass(kw_only=True)
class StartToAfterGargoylesInFirelink(Segment):
    options: Options

    def __post_init__(self) -> None:
        SHARDS_PER_LEVEL = [1, 1, 2, 2, 3]
        early_weapon_shards = sum(
            SHARDS_PER_LEVEL[0 : self.options.initial_upgrade]
        )

        starting = "starting equipment"
        pyromancer = "Pyromancer starting equipment"
        super().__post_init__()
        self.add_steps(
            Receive(Item.DARKSIGN, detail=starting),
            Receive("Straight Sword Hilt", detail=starting),
            AutoEquip("Straight Sword Hilt", "Right Hand", detail=starting),
            Receive("Tattered Cloth Hood", detail=pyromancer),
            Receive("Tattered Cloth Robe", detail=pyromancer),
            Receive("Tattered Cloth Manchette", detail=pyromancer),
            Receive("Heavy Boots", detail=pyromancer),
            AutoEquip("Tattered Cloth Hood", "Head", detail=pyromancer),
            AutoEquip("Tattered Cloth Robe", "Torso", detail=pyromancer),
            AutoEquip("Tattered Cloth Manchette", "Arms", detail=pyromancer),
            AutoEquip("Heavy Boots", "Legs", detail=pyromancer),
            Region("Northern Undead Asylum"),
            AutoBonfire("Undead Asylum Dungeon Cell"),
            Loot("Dungeon Cell Key"),
            UnEquip("Torso", detail="First ladder or big door."),
            UnEquip("Arms", detail="First ladder or big door."),
            Loot("Hand Axe"),
            Equip("Hand Axe", "Right Hand", detail="Fog gate before Oscar"),
            TalkTo("Oscar of Astora", detail="Behind wall boulder breaks"),
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
            conditional(
                not self.options.loots_firelink_at_start,
                notes=[
                    "Firelink <b>IS NOT</b> looted at start;"
                    f" goes straight to {andre}."
                ],
            ),
            conditional(
                self.options.loots_firelink_at_start,
                Loot(
                    Item.HUMANITY,
                    count=3,
                    humanities=1,
                    detail="side of well, get during Firelink loot route.",
                    condition=(
                        self.options.firelink.loot_well_humanity
                        and not self.options.uses_reinforced_club
                    ),
                    notes=[
                        "3 humanities at Firelink well looted immediately."
                    ],
                ),
                Loot(
                    "Soul of a Lost Undead",
                    souls=200,
                    detail="upper elevator",
                    condition=self.options.firelink.loot_elevator_soul,
                ),
                Jump(
                    "off ledge to hidden chests",
                    condition=self.options.firelink.loot_homeward_bones,
                ),
                Loot(
                    Item.BONE,
                    count=6,
                    detail="hidden chest",
                    condition=self.options.firelink.loot_homeward_bones,
                ),
                Equip(
                    Item.BONE,
                    "Item 5",
                    detail="immediately",
                    condition=self.options.firelink.loot_homeward_bones,
                ),
                Loot(
                    "Large Soul of a Lost Undead",
                    souls=400,
                    detail="middle of graveyard",
                    condition=self.options.firelink.loot_graveyard_souls,
                ),
                Loot(
                    "Large Soul of a Lost Undead",
                    souls=400,
                    detail="start of graveyard",
                    condition=self.options.firelink.loot_graveyard_souls,
                ),
                Use(
                    Item.BONE,
                    condition=self.options.firelink.loot_graveyard_souls,
                ),
                notes=["Firelink is looted upon arrival."],
            ),
            conditional(
                self.options.uses_reinforced_club,
                Region("Firelink Shrine"),
                Loot(
                    Item.HUMANITY,
                    count=3,
                    humanities=1,
                    detail=("side of well, get on way to get Reinforced Club"),
                    condition=self.options.firelink.loot_well_humanity,
                    notes=[
                        (
                            "3 humanities at Firelink well looted on way to"
                            " get Reinforced Club."
                        )
                    ],
                ),
                RunTo("Undead Burg"),
                Region("Undead Burg"),
                Buy("Reinforced Club", souls=350, detail="Undead Merchant"),
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
                condition=self.options.new_londo_ruins.loot_elevator_soul,
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
                condition=self.options.uses_reinforced_club,
            ),
            Equip(
                "Soul of a Nameless Soldier",
                "Item 2",
                detail=rtsr_ladder,
                condition=self.options.new_londo_ruins.loot_elevator_soul,
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
                condition=self.options.new_londo_ruins.loot_elevator_soul,
            ),
            Equip("Red Tearstone Ring", "Ring 2", detail=basin_elevator),
            Region("Darkroot Basin"),
            Loot("Grass Crest Shield"),
            Equip("Grass Crest Shield", "Left Hand", detail="immediately"),
            Kill(
                "Black Knight",
                souls=1800,
                detail=(
                    "by Grass Crest Shield."
                    + (
                        (
                            '<br/><span class="warning">SKIPPING THIS MEANS'
                            " ONLY HAVING A +3 WEAPON</span>"
                        )
                        if self.options.initial_upgrade == 4
                        else ""
                    )
                ),
                condition=self.options.darkroot_basin.kill_black_knight,
                optional=self.options.initial_upgrade == 4,
                notes=(
                    [
                        (
                            "Black Knight in Darkroot Basin <b>PRECISELY</b>"
                            " determines whether you can afford upgrading your"
                            f" {self.options.early_weapon} to +3 or +4."
                        )
                    ]
                    if self.options.initial_upgrade == 4
                    else [
                        (
                            "Black Knight in Darkroot Basin"
                            " <b>MUST</b> be killed."
                        )
                    ]
                ),
            ),
            conditional(
                not self.options.darkroot_basin.kill_black_knight,
                notes=[
                    (
                        "Black Knight in Darkroot Basin"
                        " <b>DOES NOT</b> need killed."
                    )
                ],
            ),
            RunTo(
                "Undead Parish",
                detail=(
                    ""
                    if self.options.darkroot_basin.kill_black_knight
                    else "no need to kill Black Knight"
                ),
            ),
            Region("Undead Parish"),
            Buy(
                "Battle Axe",
                souls=1000,
                detail=andre,
                condition=self.options.uses_battle_axe,
            ),
            conditional(
                self.options.initial_upgrade > 0,
                Buy(
                    Item.TITANITE_SHARD,
                    count=early_weapon_shards,
                    souls=800,
                    detail=andre,
                ),
                UpgradeCost(
                    (
                        f"{self.options.early_weapon}"
                        f" +0-{self.options.initial_upgrade}"
                    ),
                    souls=200 * self.options.initial_upgrade,
                    items=Counter({Item.TITANITE_SHARD: early_weapon_shards}),
                    detail=andre,
                ),
                Equip(
                    "Battle Axe",
                    "Right Hand",
                    detail=andre,
                    condition=self.options.uses_battle_axe,
                ),
            ),
            Loot(
                "Fire Keeper Soul",
                humanities=5,
                detail="on altar behind Berenike Knight",
                condition=self.options.undead_parish.loot_fire_keeper_soul,
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
                oswald,
                detail="TODO: RTSR setup: heal, fall down both ladders",
                condition=(
                    self.options.npc.kill_oswald
                    or not self.options.firelink.loot_homeward_bones
                ),
            ),
            Buy(
                Item.BONE,
                count=self.options.bone_count_if_from_oswald,
                souls=500,
                detail=oswald,
                condition=not self.options.firelink.loot_homeward_bones,
                notes=[
                    f"{oswald} <b>MUST</b> be visited to buy {Item.BONE}s."
                ],
            ),
            Kill(oswald, souls=2000, condition=self.options.npc.kill_oswald),
            Loot(
                Item.TWIN_HUMANITIES,
                count=2,
                humanities=2,
                detail=oswald,
                condition=self.options.npc.kill_oswald,
            ),
            Equip(
                Item.BONE,
                "Item 5",
                detail="immediately",
                condition=not self.options.firelink.loot_homeward_bones,
            ),
            Use(Item.BONE),
        )


@dataclass
class FirelinkToQuelaag(Segment):
    def __post_init__(self) -> None:
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
    options: Options

    def __post_init__(self) -> None:
        super().__post_init__()
        self.add_steps(
            Region("Firelink Shrine"),
            Loot(
                Item.HUMANITY,
                count=3,
                humanities=1,
                detail=f"side of well, get on way to {parish_elevator}.",
                condition=(
                    self.options.firelink.loot_well_humanity
                    and not self.options.loots_firelink_at_start
                    and not self.options.uses_reinforced_club
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
            BonfireSit(
                "Undead Parish",
                detail="for warping to later, and safety for Sen's Fortress",
            ),
            RunTo("Sen's Fortress"),
            Region("Sen's Fortress"),
            RunTo("room before 2nd boulder"),
            WaitFor("boulder to pass", detail="hitting enemy in room 5 times"),
            RunTo("top of ramp", detail="must go IMMEDIATELY after boulder"),
            RunTo("fog gate at top of Sen's Fortress"),
            conditional(
                self.options.ring.slumbering_dragoncrest_ring,
                BonfireSit(
                    "Sen's Fortress",
                    detail=f"to bone back after getting {slumbering}",
                ),
                RunTo(
                    "hole at dead end below bonfire and to the right",
                    detail="fall down it",
                ),
                Loot(slumbering),
                Use(Item.BONE),
            ),
            conditional(
                not self.options.ring.slumbering_dragoncrest_ring,
                BonfireSit(
                    "Sen's Fortress",
                    detail="safety for Iron Golem",
                    optional=True,
                ),
            ),
        )


@dataclass
class SensFortressToAnorLondoResidence(Segment):
    options: Options

    def __post_init__(self) -> None:
        super().__post_init__()
        self.add_steps(
            Region("Sen's Fortress"),
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
            conditional(
                self.options.all_bosses,
                BonfireSit(
                    "Anor Londo", detail="safety for rafters", optional=True
                ),
            ),
            conditional(
                not self.options.all_bosses,
                BonfireSit(
                    "Anor Londo", detail=f"so you can warp back for {seath}"
                ),
            ),
            BonfireSit(
                "Anor Londo", detail="safety for rafters", optional=True
            ),
            RunTo("elevator"),
            UseMenu("Core of an Iron Golem", detail="elevator"),
            RunTo("other end of rafters"),
            Activate("Bridge lever (1st time to level)"),
            Equip(
                slumbering,
                slot="Ring 1",
                detail="while pushing bridge lever",
                condition=self.options.ring.slumbering_dragoncrest_ring,
            ),
            conditional(
                self.options.all_bosses,
                Activate("Bridge lever (2nd time for Darkmoon Tomb)"),
                RunTo("bottom of the stairs"),
                BonfireSit(
                    "Darkmoon Tomb",
                    detail=(
                        f"so you can warp back for {gwyndolin} and {priscilla}"
                    ),
                ),
                RunTo("top of the stairs"),
                Activate("Bridge lever (3rd time to re-level)"),
            ),
            RunTo("sniper ledge"),
            Kill(
                "Silver Knight",
                souls=1300,
                detail="bait melee then run to make him fall",
            ),
            BonfireSit("Anor Londo Residence"),
        )


@dataclass
class GetAndUpgradeBlacksmithGiantHammer(Segment):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.add_steps(
            Region("Anor Londo"),
            RunTo("Giant Blacksmith"),
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
            UpgradeCost(
                "Blacksmith Giant Hammer +0-5",
                souls=10000,
                items=Counter({Item.TWINKLING_TITANITE: 10}),
                detail="(Bonfire) Blacksmith Giant Hammer +0-5",
            ),
            Equip(
                "Blacksmith Giant Hammer",
                "Right Hand",
                detail="could wait until O&S fog gate",
            ),
        )


@dataclass
class AnorLondoResidenceToSif(Segment):
    options: Options

    def __post_init__(self) -> None:
        super().__post_init__()
        self.add_steps(
            RunTo("Spiral Stairs and jump out for shortcut"),
            FallDamage(
                "Jumping from upper stairs over the rail of the flat section"
                "Landing on the ground, rolling immediately.",
                detail="RTSR setup (1/2)",
            ),
            RunTo("Top of stairs by where you entered the room"),
            FallDamage(
                "Jumping from top of stairs toward boss fog gate"
                "rolling immediately.",
                detail="RTSR setup (2/2)",
            ),
            Kill(
                O_and_S,
                souls=50000,
                detail=(
                    "Kill Smough first"
                    if self.options.boss.kill_smough_first
                    else "Kill Ornstein first"
                ),
            ),
            Receive(
                "Soul of Smough",
                souls=12000,
                detail=O_and_S,
                condition=not self.options.boss.kill_smough_first,
            ),
            Receive(
                "Soul of Ornstein",
                souls=12000,
                detail=O_and_S,
                condition=self.options.boss.kill_smough_first,
            ),
            # Loot(
            #    "Leo Ring",
            #    detail=f"({O_and_S}) on the ground",
            #    condition=self.options.boss.kill_smough_first,
            # ),
            TalkTo("Gwynevere"),
            Receive("Lordvessel", detail="Gwynevere"),
            Use(Item.BONE),
            WarpTo("Undead Parish"),
            Buy("Crest of Artorias", souls=20000, detail=andre),
            RunTo("Darkroot Garden door"),
            Region("Darkroot Garden"),
            Activate("Darkroot Garden door", detail="using Crest of Artorias"),
            Equip(
                Item.DARKSIGN,
                "Item 5",
                detail="while door is opening (no need for bones anymore)",
                expected_to_replace=Item.BONE,
            ),
        )


@dataclass(kw_only=True)
class ToDoSegment(Segment):
    options: Options

    def __post_init__(self) -> None:
        super().__post_init__()
        self.add_steps(
            Region("TODO"),
            Receive(Item.HUMANITY, humanities=1, detail=O_and_S),
            Kill("Pinwheel", souls=15000),
            Receive("Rite of Kindling", detail="Pinwheel"),
            Receive(Item.HUMANITY, humanities=1, detail="Pinwheel"),
            Receive(Item.BONE, detail="Pinwheel"),
            Kill(nito, souls=60000),
            Receive("Lord Soul", detail=nito),
            conditional(
                not self.options.boss.wait_for_nito_drops,
                notes=[f"1 slow {Item.HUMANITY} skipped from {nito}."],
            ),
            conditional(
                self.options.boss.wait_for_nito_drops,
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
                not self.options.boss.wait_for_sif_drops,
                notes=[
                    f"1 slow {Item.HUMANITY} and {Item.BONE}"
                    f" skipped from {sif}."
                ],
            ),
            conditional(
                self.options.boss.wait_for_sif_drops,
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
                not self.options.boss.wait_for_four_kings_drops,
                notes=[f"4 slow {Item.HUMANITY} skipped from {four_kings}."],
            ),
            conditional(
                self.options.boss.wait_for_four_kings_drops,
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
                condition=self.options.npc.kill_darkmoon_knightess,
            ),
            Loot(
                "Fire Keeper Soul",
                detail="Darkmoon Knightess",
                condition=self.options.npc.kill_darkmoon_knightess,
            ),
            Kill(seath, souls=60000),
            Receive("Bequeathed Lord Soul Shard", detail=seath),
            conditional(
                not self.options.boss.wait_for_seath_drops,
                notes=[f"1 slow {Item.HUMANITY} skipped from {seath}."],
            ),
            conditional(
                self.options.boss.wait_for_seath_drops,
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
                condition=self.options.npc.kill_patches,
            ),
            Loot(
                Item.HUMANITY,
                count=4,
                humanities=1,
                detail="Patches",
                condition=self.options.npc.kill_patches,
            ),
            Kill(petrus, souls=1000, condition=self.options.npc.kill_petrus),
            Loot(
                Item.HUMANITY,
                count=2,
                humanities=1,
                detail=petrus,
                condition=self.options.npc.kill_petrus,
            ),
            Kill(andre, souls=1000, condition=self.options.npc.kill_andre),
            Loot(
                Item.HUMANITY,
                count=3,
                humanities=1,
                detail=andre,
                condition=self.options.npc.kill_andre,
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


class SL1RangelessGlitchless(Route):
    def __init__(self, options: Options):
        super().__init__(
            name=(f"SL1 Rangeless Glitchless ({options.display_name})"),
            segment=Segment(
                notes=(
                    [
                        "TODO: fix RTSR setup for Gargoyles",
                        "TODO: best path past boulders in Sen's Fortress",
                        "TODO: when to swap darksign for bones",
                        "TODO: Crest of Artorias cost.",
                        "TODO: de-minify output.",
                    ]
                    + options.notes
                )
            ),
            damage_tables=options.damage_tables,
            hit_lookup=SL1_HIT_LOOKUP,
        )

        self.segment.add_steps(
            StartToAfterGargoylesInFirelink(options=options),
            FirelinkToQuelaag(),
            FirelinkToSensFortress(options=options),
            SensFortressToAnorLondoResidence(options=options),
            GetAndUpgradeBlacksmithGiantHammer(),
            AnorLondoResidenceToSif(options=options),
            ####################
            ToDoSegment(options=options),
        )


EXPORTED_ROUTES: list[Route] = [
    SL1RangelessGlitchless(options=Variation.REINFORCED_CLUB.options),
    SL1RangelessGlitchless(options=Variation.BATTLE_AXE_PLUS_4_OR_3.options),
    SL1RangelessGlitchless(
        options=Variation.BATTLE_AXE_PLUS_4_SKIPPING_BLACK_KNIGHT.options
    ),
]

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
# - determine when to loot Lautrec, or how to replace him (quitoutless)
# - add ability to estimate time for a segment
# - fix RTSR setup for gargoyles

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
