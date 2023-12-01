from .route import Enemy, Hit, HitType

SL1_HIT_LOOKUP: dict[str, dict[Enemy, dict[HitType, Hit]]] = {
    "Hand Axe +0": {
        Enemy.BLACK_KNIGHT_DARKROOT_BASIN: {
            HitType.HEAVY_1H: Hit(14, with_rtsr=31),
            HitType.WEAK_1H: Hit(10, with_rtsr=20),
            HitType.HEAVY_2H: Hit(28, with_rtsr=72),
            HitType.WEAK_2H: Hit(16, with_rtsr=37),
            HitType.RIPOSTE_1H: Hit(5 + 57, with_rtsr=8 + 146),
            HitType.RIPOSTE_2H: Hit(6 + 75, with_rtsr=10 + 179),
        }
    },
    "Reinforced Club +0": {
        Enemy.BLACK_KNIGHT_DARKROOT_BASIN: {
            HitType.HEAVY_1H: Hit(31, with_rtsr=82),
            HitType.WEAK_1H: Hit(15, with_rtsr=33),
            HitType.HEAVY_2H: Hit(49, with_rtsr=134),
            HitType.WEAK_2H: Hit(28, with_rtsr=71),
            HitType.RIPOSTE_1H: Hit(6 + 95, with_rtsr=11 + 209),
            HitType.RIPOSTE_2H: Hit(7 + 127, with_rtsr=14 + 263),
        }
    },
    "Reinforced Club +5": {
        Enemy.BELL_GARGOYLES: {
            HitType.HEAVY_1H: Hit(161, with_rtsr=275),
            HitType.WEAK_1H: Hit(84, with_rtsr=170),
            HitType.HEAVY_2H: Hit(217, with_rtsr=358),
            HitType.WEAK_2H: Hit(185, with_rtsr=259),
        },
        Enemy.LAUTREC: {
            HitType.HEAVY_1H: Hit(91, with_rtsr=208),
            HitType.WEAK_1H: Hit(36, with_rtsr=100),
            HitType.HEAVY_2H: Hit(145, with_rtsr=295),
            HitType.WEAK_2H: Hit(80, with_rtsr=191),
            HitType.RIPOSTE_1H: Hit(12 + 220, with_rtsr=25 + 398),
            HitType.RIPOSTE_2H: Hit(15 + 276, with_rtsr=35 + 469),
        },
        Enemy.QUELAAG: {HitType.WEAK_2H: Hit(77, with_rtsr=187)},
        Enemy.IRON_GOLEM: {HitType.WEAK_2H: Hit(with_rtsr=159)},
    },
    "Battle Axe +4": {
        Enemy.BELL_GARGOYLES: {
            HitType.HEAVY_1H: Hit(107, with_rtsr=205),
            HitType.WEAK_1H: Hit(70, with_rtsr=130),
            HitType.HEAVY_2H: Hit(175, with_rtsr=295),
            HitType.WEAK_2H: Hit(122, with_rtsr=226),
        },
        Enemy.QUELAAG: {HitType.WEAK_2H: Hit(57, with_rtsr=149)},
        Enemy.IRON_GOLEM: {HitType.WEAK_2H: Hit(with_rtsr=78)},
    },
    "Battle Axe +3": {
        Enemy.BELL_GARGOYLES: {
            HitType.HEAVY_1H: Hit(93, with_rtsr=184),
            HitType.WEAK_1H: Hit(54, with_rtsr=115),
            HitType.HEAVY_2H: Hit(156, with_rtsr=268),
            HitType.WEAK_2H: Hit(107, with_rtsr=205),
        },
        Enemy.QUELAAG: {
            # HitType.WEAK_2H: Hit(),
        },
        Enemy.IRON_GOLEM: {
            # HitType.WEAK_2H: Hit(),
        },
    },
}
