from __future__ import annotations

from .route import html_page
from .sl1 import SL1MeleeOnlyGlitchless


def main() -> int:
    route = SL1MeleeOnlyGlitchless()

    print(html_page(route))
    return 0
