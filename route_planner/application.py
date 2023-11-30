from __future__ import annotations

from . import report
from .sl1 import SL1MeleeOnlyGlitchless, Variation


def main() -> int:
    output_dir = "docs"

    route_names = set()

    with open(f"{output_dir}/index.html", "w") as index:
        index.write("<h1>Route Index</h1><ul>")
        for route in [
            SL1MeleeOnlyGlitchless(variation=Variation.REINFORCED_CLUB),
            SL1MeleeOnlyGlitchless(variation=Variation.BATTLE_AXE_PLUS_4_OR_3),
            SL1MeleeOnlyGlitchless(
                variation=Variation.BATTLE_AXE_PLUS_4_SKIPPING_BLACK_KNIGHT
            ),
        ]:
            filename = (
                "".join(ch for ch in route.name if ch.isalnum()) + ".html"
            )

            with open(f"{output_dir}/{filename}", "w") as route_file:
                if filename in route_names:
                    raise RuntimeError(
                        f"Multiple routes with the same name: {filename}"
                    )
                route_names.add(filename)
                route_file.write(
                    report.page(report.route(route), title=route.name)
                )

            index.write(f'<li><a href="{filename}">{route.name}</a></li>\n')
        index.write("</ul>")
    return 0
