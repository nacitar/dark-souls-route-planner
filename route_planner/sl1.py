from typing import Sequence

from .route import Enemy, Hit, HitType


def _sl1_hittype_by_melee_damage() -> dict[HitType, int]:
    melee_types = set(HitType.melee_types())
    ordered_by_damage = [
        HitType.WEAK_1H,
        HitType.HEAVY_1H,
        HitType.WEAK_2H,
        HitType.JUMPING_1H,  # order of entry may deviate from expectations
        HitType.HEAVY_2H,
        HitType.JUMPING_2H,
        HitType.BACKSTAB_1H,
        HitType.BACKSTAB_2H,
        HitType.RIPOSTE_1H,
        HitType.RIPOSTE_2H,
    ]
    melee_types.difference_update(ordered_by_damage)
    if melee_types:
        raise AssertionError(
            "Some melee types are not listed: "
            + ",".join([entry.name for entry in melee_types])
        )
    return {
        hit_type: index for index, hit_type in enumerate(ordered_by_damage)
    }


_SL1_HITTYPE_BY_MELEE_DAMAGE = _sl1_hittype_by_melee_damage()


def sl1_ordered_by_melee_damage(hit_types: Sequence[HitType]) -> list[HitType]:
    return sorted(
        hit_types, key=lambda hit_type: _SL1_HITTYPE_BY_MELEE_DAMAGE[hit_type]
    )


SL1_HIT_LOOKUP: dict[str, dict[Enemy, dict[HitType, Hit]]] = {
    "Hand Axe +0": {
        Enemy.BLACK_KNIGHT_DARKROOT_BASIN: {
            HitType.WEAK_1H: Hit(10, with_rtsr=20),
            HitType.HEAVY_1H: Hit(14, with_rtsr=31),
            HitType.JUMPING_1H: Hit(21, with_rtsr=50),
            HitType.WEAK_2H: Hit(16, with_rtsr=37),
            HitType.HEAVY_2H: Hit(28, with_rtsr=72),
            HitType.JUMPING_2H: Hit(30, with_rtsr=78),
            HitType.BACKSTAB_1H: Hit(5 + 33, with_rtsr=8 + 90),
            HitType.BACKSTAB_2H: Hit(6 + 42, with_rtsr=10 + 116),
            HitType.RIPOSTE_1H: Hit(5 + 57, with_rtsr=8 + 146),
            HitType.RIPOSTE_2H: Hit(6 + 75, with_rtsr=10 + 179),
        }
    },
    "Reinforced Club +0": {
        Enemy.BLACK_KNIGHT_DARKROOT_BASIN: {
            HitType.WEAK_1H: Hit(15, with_rtsr=33),
            HitType.HEAVY_1H: Hit(20, with_rtsr=50),
            HitType.JUMPING_1H: Hit(31, with_rtsr=82),
            HitType.WEAK_2H: Hit(28, with_rtsr=71),
            HitType.HEAVY_2H: Hit(45, with_rtsr=126),
            HitType.JUMPING_2H: Hit(49, with_rtsr=134),
            HitType.BACKSTAB_1H: Hit(6 + 52, with_rtsr=11 + 138),
            HitType.BACKSTAB_2H: Hit(7 + 74, with_rtsr=14 + 177),
            HitType.RIPOSTE_1H: Hit(6 + 95, with_rtsr=11 + 209),
            HitType.RIPOSTE_2H: Hit(7 + 127, with_rtsr=14 + 263),
        }
    },
    "Reinforced Club +5": {
        Enemy.BELL_GARGOYLES: {
            HitType.WEAK_1H: Hit(84, with_rtsr=170),
            HitType.HEAVY_1H: Hit(112, with_rtsr=232),
            HitType.JUMPING_1H: Hit(161, with_rtsr=275),
            HitType.WEAK_2H: Hit(149, with_rtsr=259),
            HitType.HEAVY_2H: Hit(208, with_rtsr=343),
            HitType.JUMPING_2H: Hit(217, with_rtsr=358),
        },
        Enemy.OSWALD: {
            HitType.WEAK_1H: Hit(76, with_rtsr=159),
            HitType.HEAVY_1H: Hit(103, with_rtsr=199),
            HitType.JUMPING_1H: Hit(150, with_rtsr=271),
            HitType.WEAK_2H: Hit(139, with_rtsr=256),
            HitType.HEAVY_2H: Hit(199, with_rtsr=333),
            HitType.JUMPING_2H: Hit(209, with_rtsr=348),
            HitType.BACKSTAB_1H: Hit(19 + 204, with_rtsr=54 + 337),
            HitType.BACKSTAB_2H: Hit(27 + 244, with_rtsr=73 + 403),
            HitType.RIPOSTE_1H: Hit(19 + 269, with_rtsr=54 + 451),
            HitType.RIPOSTE_2H: Hit(27 + 322, with_rtsr=73 + 538),
        },
        Enemy.PETRUS: {
            HitType.WEAK_1H: Hit(75, with_rtsr=157),
            HitType.HEAVY_1H: Hit(101, with_rtsr=197),
            HitType.JUMPING_1H: Hit(148, with_rtsr=270),
            HitType.WEAK_2H: Hit(136, with_rtsr=254),
            HitType.HEAVY_2H: Hit(196, with_rtsr=331),
            HitType.JUMPING_2H: Hit(206, with_rtsr=345),
            HitType.BACKSTAB_1H: Hit(19 + 202, with_rtsr=51 + 355),
            HitType.BACKSTAB_2H: Hit(26 + 243, with_rtsr=71 + 400),
            HitType.RIPOSTE_1H: Hit(19 + 267, with_rtsr=51 + 448),
            HitType.RIPOSTE_2H: Hit(26 + 320, with_rtsr=71 + 535),
        },
        Enemy.LAUTREC: {
            HitType.WEAK_1H: Hit(36, with_rtsr=100),
            HitType.JUMPING_1H: Hit(91, with_rtsr=208),
            HitType.HEAVY_1H: Hit(62, with_rtsr=159),
            HitType.WEAK_2H: Hit(80, with_rtsr=191),
            HitType.JUMPING_2H: Hit(145, with_rtsr=295),
            HitType.HEAVY_2H: Hit(136, with_rtsr=280),
            HitType.BACKSTAB_1H: Hit(12 + 146, with_rtsr=25 + 292),
            HitType.BACKSTAB_2H: Hit(15 + 189, with_rtsr=35 + 357),
            HitType.RIPOSTE_1H: Hit(12 + 220, with_rtsr=25 + 398),
            HitType.RIPOSTE_2H: Hit(15 + 276, with_rtsr=35 + 469),
        },
        Enemy.QUELAAG: {
            HitType.WEAK_1H: Hit(35, with_rtsr=96),
            HitType.HEAVY_1H: Hit(53, with_rtsr=138),
            HitType.JUMPING_1H: Hit(87, with_rtsr=204),
            HitType.WEAK_2H: Hit(68, with_rtsr=166),
            HitType.HEAVY_2H: Hit(133, with_rtsr=276),
            HitType.JUMPING_2H: Hit(141, with_rtsr=291),
        },
        Enemy.IRON_GOLEM: {
            HitType.WEAK_1H: Hit(29, with_rtsr=72),
            HitType.HEAVY_1H: Hit(41, with_rtsr=129),
            HitType.JUMPING_1H: Hit(66, with_rtsr=175),
            HitType.WEAK_2H: Hit(59, with_rtsr=159),
            HitType.HEAVY_2H: Hit(103, with_rtsr=242),
            HitType.JUMPING_2H: Hit(113, with_rtsr=257),
        },
        Enemy.GIANT_BLACKSMITH: {
            HitType.WEAK_1H: Hit(42, with_rtsr=115),
            HitType.HEAVY_1H: Hit(66, with_rtsr=156),
            HitType.JUMPING_1H: Hit(108, with_rtsr=227),
            HitType.WEAK_2H: Hit(87, with_rtsr=209),
            HitType.HEAVY_2H: Hit(151, with_rtsr=299),
            HitType.JUMPING_2H: Hit(160, with_rtsr=314),
        },
        Enemy.MIMIC_OCCULT_CLUB: {
            HitType.WEAK_1H: Hit(37, with_rtsr=104),
            HitType.HEAVY_1H: Hit(57, with_rtsr=144),
            HitType.JUMPING_1H: Hit(94, with_rtsr=212),
            HitType.WEAK_2H: Hit(83, with_rtsr=194),
            HitType.HEAVY_2H: Hit(139, with_rtsr=284),
            HitType.JUMPING_2H: Hit(147, with_rtsr=299),
        },
        Enemy.DARKMOON_KNIGHTESS: {
            HitType.WEAK_1H: Hit(29, with_rtsr=75),
            HitType.HEAVY_1H: Hit(43, with_rtsr=134),
            HitType.JUMPING_1H: Hit(69, with_rtsr=180),
            HitType.WEAK_2H: Hit(61, with_rtsr=164),
            HitType.HEAVY_2H: Hit(108, with_rtsr=248),
            HitType.JUMPING_2H: Hit(118, with_rtsr=262),
            HitType.BACKSTAB_1H: Hit(11 + 124, with_rtsr=21 + 262),
            HitType.BACKSTAB_2H: Hit(13 + 163, with_rtsr=28 + 329),
            HitType.RIPOSTE_1H: Hit(11 + 192, with_rtsr=21 + 376),
            HitType.RIPOSTE_2H: Hit(13 + 246, with_rtsr=28 + 454),
        },
    },
    "Battle Axe +4": {
        Enemy.BELL_GARGOYLES: {
            HitType.WEAK_1H: Hit(70, with_rtsr=130),
            HitType.HEAVY_1H: Hit(107, with_rtsr=205),
            HitType.JUMPING_1H: Hit(138, with_rtsr=247),
            HitType.WEAK_2H: Hit(122, with_rtsr=226),
            HitType.HEAVY_2H: Hit(175, with_rtsr=295),
            HitType.JUMPING_2H: Hit(184, with_rtsr=307),
        },
        Enemy.OSWALD: {
            HitType.WEAK_1H: Hit(59, with_rtsr=125),
            HitType.HEAVY_1H: Hit(102, with_rtsr=200),
            HitType.JUMPING_1H: Hit(132, with_rtsr=244),
            HitType.WEAK_2H: Hit(116, with_rtsr=221),
            HitType.HEAVY_2H: Hit(169, with_rtsr=290),
            HitType.JUMPING_2H: Hit(178, with_rtsr=302),
            HitType.BACKSTAB_1H: Hit(16 + 182, with_rtsr=45 + 303),
            HitType.BACKSTAB_2H: Hit(21 + 213, with_rtsr=60 + 350),
            HitType.RIPOSTE_1H: Hit(16 + 243, with_rtsr=45 + 405),
            HitType.RIPOSTE_2H: Hit(22 + 279, with_rtsr=60 + 468),
        },
        Enemy.PETRUS: {
            HitType.WEAK_1H: Hit(60, with_rtsr=133),
            HitType.HEAVY_1H: Hit(96, with_rtsr=193),
            HitType.JUMPING_1H: Hit(126, with_rtsr=239),
            HitType.WEAK_2H: Hit(110, with_rtsr=215),
            HitType.HEAVY_2H: Hit(162, with_rtsr=287),
            HitType.JUMPING_2H: Hit(171, with_rtsr=297),
            HitType.BACKSTAB_1H: Hit(15 + 176, with_rtsr=40 + 297),
            HitType.BACKSTAB_2H: Hit(20 + 208, with_rtsr=54 + 344),
            HitType.RIPOSTE_1H: Hit(15 + 241, with_rtsr=40 + 397),
            HitType.RIPOSTE_2H: Hit(20 + 274, with_rtsr=54 + 459),
        },
        Enemy.LAUTREC: {
            HitType.WEAK_1H: Hit(28, with_rtsr=74),
            HitType.HEAVY_1H: Hit(47, with_rtsr=129),
            HitType.JUMPING_1H: Hit(68, with_rtsr=171),
            HitType.WEAK_2H: Hit(50, with_rtsr=149),
            HitType.HEAVY_2H: Hit(100, with_rtsr=224),
            HitType.JUMPING_2H: Hit(109, with_rtsr=237),
            HitType.BACKSTAB_1H: Hit(10 + 119, with_rtsr=20 + 247),
            HitType.BACKSTAB_2H: Hit(12 + 148, with_rtsr=26 + 296),
            HitType.RIPOSTE_1H: Hit(10 + 182, with_rtsr=20 + 349),
            HitType.RIPOSTE_2H: Hit(12 + 222, with_rtsr=26 + 405),
        },
        Enemy.QUELAAG: {
            HitType.WEAK_1H: Hit(25, with_rtsr=66),
            HitType.HEAVY_1H: Hit(47, with_rtsr=130),
            HitType.JUMPING_1H: Hit(68, with_rtsr=172),
            HitType.WEAK_2H: Hit(57, with_rtsr=149),
            HitType.HEAVY_2H: Hit(101, with_rtsr=225),
            HitType.JUMPING_2H: Hit(110, with_rtsr=238),
        },
        Enemy.IRON_GOLEM: {
            HitType.WEAK_1H: Hit(19, with_rtsr=36),
            HitType.HEAVY_1H: Hit(28, with_rtsr=65),
            HitType.JUMPING_1H: Hit(37, with_rtsr=94),
            HitType.WEAK_2H: Hit(32, with_rtsr=78),
            HitType.HEAVY_2H: Hit(51, with_rtsr=137),
            HitType.JUMPING_2H: Hit(55, with_rtsr=149),
        },
        Enemy.GIANT_BLACKSMITH: {
            HitType.WEAK_1H: Hit(30, with_rtsr=84),
            HitType.HEAVY_1H: Hit(58, with_rtsr=147),
            HitType.JUMPING_1H: Hit(86, with_rtsr=193),
            HitType.WEAK_2H: Hit(71, with_rtsr=169),
            HitType.HEAVY_2H: Hit(120, with_rtsr=248),
            HitType.JUMPING_2H: Hit(128, with_rtsr=261),
        },
        Enemy.MIMIC_OCCULT_CLUB: {
            HitType.WEAK_1H: Hit(30, with_rtsr=80),
            HitType.HEAVY_1H: Hit(51, with_rtsr=135),
            HitType.JUMPING_1H: Hit(74, with_rtsr=179),
            HitType.WEAK_2H: Hit(61, with_rtsr=156),
            HitType.HEAVY_2H: Hit(109, with_rtsr=233),
            HitType.JUMPING_2H: Hit(117, with_rtsr=246),
        },
        Enemy.DARKMOON_KNIGHTESS: {
            HitType.WEAK_1H: Hit(24, with_rtsr=57),
            HitType.HEAVY_1H: Hit(38, with_rtsr=100),
            HitType.JUMPING_1H: Hit(53, with_rtsr=146),
            HitType.WEAK_2H: Hit(44, with_rtsr=122),
            HitType.HEAVY_2H: Hit(76, with_rtsr=195),
            HitType.JUMPING_2H: Hit(83, with_rtsr=207),
            HitType.BACKSTAB_1H: Hit(9 + 94, with_rtsr=17 + 218),
            HitType.BACKSTAB_2H: Hit(11 + 126, with_rtsr=21 + 267),
            HitType.RIPOSTE_1H: Hit(9 + 157, with_rtsr=17 + 321),
            HitType.RIPOSTE_2H: Hit(11 + 195, with_rtsr=21 + 383),
        },
    },
    "Battle Axe +3": {
        Enemy.BELL_GARGOYLES: {
            HitType.WEAK_1H: Hit(54, with_rtsr=115),
            HitType.HEAVY_1H: Hit(93, with_rtsr=184),
            HitType.JUMPING_1H: Hit(122, with_rtsr=226),
            HitType.WEAK_2H: Hit(107, with_rtsr=205),
            HitType.HEAVY_2H: Hit(156, with_rtsr=268),
            HitType.JUMPING_2H: Hit(164, with_rtsr=280),
        },
        Enemy.OSWALD: {
            HitType.WEAK_1H: Hit(49, with_rtsr=123),
            HitType.HEAVY_1H: Hit(88, with_rtsr=179),
            HitType.JUMPING_1H: Hit(116, with_rtsr=222),
            HitType.WEAK_2H: Hit(101, with_rtsr=200),
            HitType.HEAVY_2H: Hit(150, with_rtsr=266),
            HitType.JUMPING_2H: Hit(158, with_rtsr=276),
            HitType.BACKSTAB_1H: Hit(14 + 163, with_rtsr=37 + 275),
            HitType.BACKSTAB_2H: Hit(18 + 193, with_rtsr=50 + 319),
            HitType.RIPOSTE_1H: Hit(14 + 223, with_rtsr=37 + 368),
            HitType.RIPOSTE_2H: Hit(18 + 254, with_rtsr=50 + 426),
        },
        Enemy.PETRUS: {
            HitType.WEAK_1H: Hit(49, with_rtsr=117),
            HitType.HEAVY_1H: Hit(83, with_rtsr=171),
            HitType.JUMPING_1H: Hit(110, with_rtsr=215),
            HitType.WEAK_2H: Hit(96, with_rtsr=193),
            HitType.HEAVY_2H: Hit(143, with_rtsr=263),
            HitType.JUMPING_2H: Hit(151, with_rtsr=274),
            HitType.BACKSTAB_1H: Hit(13 + 157, with_rtsr=33 + 270),
            HitType.BACKSTAB_2H: Hit(16 + 187, with_rtsr=45 + 313),
            HitType.RIPOSTE_1H: Hit(13 + 220, with_rtsr=33 + 361),
            HitType.RIPOSTE_2H: Hit(16 + 252, with_rtsr=45 + 418),
        },
        Enemy.LAUTREC: {
            HitType.WEAK_1H: Hit(21, with_rtsr=61),
            HitType.HEAVY_1H: Hit(39, with_rtsr=110),
            HitType.JUMPING_1H: Hit(56, with_rtsr=149),
            HitType.WEAK_2H: Hit(47, with_rtsr=129),
            HitType.HEAVY_2H: Hit(82, with_rtsr=196),
            HitType.JUMPING_2H: Hit(90, with_rtsr=208),
            HitType.BACKSTAB_1H: Hit(9 + 102, with_rtsr=17 + 218),
            HitType.BACKSTAB_2H: Hit(10 + 128, with_rtsr=22 + 264),
            HitType.RIPOSTE_1H: Hit(9 + 159, with_rtsr=17 + 314),
            HitType.RIPOSTE_2H: Hit(10 + 196, with_rtsr=22 + 369),
        },
        Enemy.QUELAAG: {
            HitType.WEAK_1H: Hit(22, with_rtsr=55),
            HitType.HEAVY_1H: Hit(40, with_rtsr=111),
            HitType.JUMPING_1H: Hit(57, with_rtsr=150),
            HitType.WEAK_2H: Hit(47, with_rtsr=129),
            HitType.HEAVY_2H: Hit(83, with_rtsr=197),
            HitType.JUMPING_2H: Hit(90, with_rtsr=209),
        },
        Enemy.IRON_GOLEM: {
            HitType.WEAK_1H: Hit(17, with_rtsr=35),
            HitType.HEAVY_1H: Hit(25, with_rtsr=55),
            HitType.JUMPING_1H: Hit(32, with_rtsr=78),
            HitType.WEAK_2H: Hit(28, with_rtsr=65),
            HitType.HEAVY_2H: Hit(44, with_rtsr=113),
            HitType.JUMPING_2H: Hit(47, with_rtsr=123),
        },
        Enemy.GIANT_BLACKSMITH: {
            HitType.WEAK_1H: Hit(25, with_rtsr=69),
            HitType.HEAVY_1H: Hit(48, with_rtsr=128),
            HitType.JUMPING_1H: Hit(71, with_rtsr=169),
            HitType.WEAK_2H: Hit(58, with_rtsr=147),
            HitType.HEAVY_2H: Hit(104, with_rtsr=219),
            HitType.JUMPING_2H: Hit(111, with_rtsr=232),
        },
        Enemy.MIMIC_OCCULT_CLUB: {
            HitType.WEAK_1H: Hit(23, with_rtsr=59),
            HitType.HEAVY_1H: Hit(42, with_rtsr=117),
            HitType.JUMPING_1H: Hit(61, with_rtsr=156),
            HitType.WEAK_2H: Hit(51, with_rtsr=135),
            HitType.HEAVY_2H: Hit(90, with_rtsr=205),
            HitType.JUMPING_2H: Hit(98, with_rtsr=217),
        },
        Enemy.DARKMOON_KNIGHTESS: {
            HitType.WEAK_1H: Hit(21, with_rtsr=48),
            HitType.HEAVY_1H: Hit(32, with_rtsr=83),
            HitType.JUMPING_1H: Hit(44, with_rtsr=122),
            HitType.WEAK_2H: Hit(38, with_rtsr=100),
            HitType.HEAVY_2H: Hit(63, with_rtsr=169),
            HitType.JUMPING_2H: Hit(68, with_rtsr=180),
            HitType.BACKSTAB_1H: Hit(8 + 77, with_rtsr=15 + 191),
            HitType.BACKSTAB_2H: Hit(10 + 104, with_rtsr=19 + 236),
            HitType.RIPOSTE_1H: Hit(8 + 136, with_rtsr=15 + 285),
            HitType.RIPOSTE_2H: Hit(10 + 170, with_rtsr=19 + 342),
        },
    },
    "Blacksmith Giant Hammer +5": {
        Enemy.MIMIC_OCCULT_CLUB: {
            HitType.WEAK_2H: Hit(358, with_rtsr=658),
            HitType.HEAVY_2H: Hit(512, with_rtsr=898),
            HitType.JUMPING_2H: Hit(537, with_rtsr=939),
        },
        Enemy.DARKMOON_KNIGHTESS: {
            HitType.WEAK_2H: Hit(321, with_rtsr=620),
            HitType.HEAVY_2H: Hit(478, with_rtsr=853),
            HitType.JUMPING_2H: Hit(503, with_rtsr=893),
            HitType.BACKSTAB_2H: Hit(68 + 600, with_rtsr=166 + 1058),
            HitType.RIPOSTE_2H: Hit(68 + 830, with_rtsr=166 + 1411),
        },
    },
}
