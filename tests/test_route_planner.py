from route_planner import __version__
from route_planner.route import HitType
from route_planner.sl1 import SL1_HIT_LOOKUP, sl1_ordered_by_melee_damage


def test_version() -> None:
    assert __version__ == "0.2.0"


def test_sl1_damage_numbers_look_reasonable() -> None:
    errors: list[str] = []
    HIT_TYPES = sl1_ordered_by_melee_damage(HitType.melee_types())
    for weapon, enemy_to_hittype_to_hit in SL1_HIT_LOOKUP.items():
        for enemy, hittype_to_hit in enemy_to_hittype_to_hit.items():
            last_damage = 0
            last_rtsr_damage = 0
            for hittype in HIT_TYPES:
                hit = hittype_to_hit.get(hittype)
                if hit is None:
                    continue
                error_root = f"{weapon} vs {enemy} with {hittype}"
                if hit.damage < last_damage:
                    errors.append(f"{error_root} of {hit.damage}")
                else:
                    last_damage = hit.damage
                if hit.with_rtsr < last_rtsr_damage:
                    errors.append(f"{error_root} of {hit.with_rtsr} with RTSR")
                else:
                    last_rtsr_damage = hit.with_rtsr
    for error in errors:
        print(f"{error} looks wrong given other provided numbers.")
    assert len(errors) == 0
