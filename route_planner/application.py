from __future__ import annotations

from .sl1 import SL1MeleeOnlyGlitchless


def main() -> int:
    route = SL1MeleeOnlyGlitchless(style="light")
    print(route._repr_html_())
    return 0
