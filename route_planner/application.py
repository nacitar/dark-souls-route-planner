from __future__ import annotations

from .sl1 import SL1MeleeOnlyGlitchless


def main() -> int:
    route = SL1MeleeOnlyGlitchless()
    for entry in route.output:
        entry.validate()
        print(entry)
    return 0
