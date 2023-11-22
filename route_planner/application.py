from __future__ import annotations

from .segment import html_page
from .sl1 import Route, SL1MeleeOnlyGlitchless


def main() -> int:
    route = Route.REINFORCED_CLUB
    # route=Route.BATTLE_AXE_PLUS4
    # route=Route.BATTLE_AXE_PLUS4_NO_BLACK_KNIGHT
    # route=Route.BATTLE_AXE_PLUS3
    segment = SL1MeleeOnlyGlitchless(route)

    print(html_page(segment, title=segment.name))
    return 0
