from __future__ import annotations

from .segment import html_page
from .sl1 import Route, SL1MeleeOnlyGlitchless


def main() -> int:
    output_dir = "docs"

    route_names = set()

    with open(f"{output_dir}/index.html", "w") as index:
        index.write("<h1>Route Index</h1><ul>")
        for segment in [
            SL1MeleeOnlyGlitchless(route=Route.REINFORCED_CLUB),
            SL1MeleeOnlyGlitchless(route=Route.BATTLE_AXE_PLUS_4_OR_3),
            SL1MeleeOnlyGlitchless(
                route=Route.BATTLE_AXE_PLUS_4_SKIPPING_BLACK_KNIGHT
            ),
        ]:
            filename = (
                "".join(ch for ch in segment.name if ch.isalnum()) + ".html"
            )

            with open(f"{output_dir}/{filename}", "w") as route_file:
                if filename in route_names:
                    raise RuntimeError(
                        f"Multiple routes with the same name: {filename}"
                    )
                route_names.add(filename)
                route_file.write(html_page(segment, title=segment.name))

            index.write(f'<li><a href="{filename}">{segment.name}</a></li>\n')
        index.write("</ul>")
    return 0
