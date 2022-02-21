from __future__ import annotations

from .sl1 import SL1MeleeOnlyGlitchless
from .route import html_page


def main() -> int:
    route = SL1MeleeOnlyGlitchless()

    print(html_page(route))
    return 0
