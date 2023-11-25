from __future__ import annotations

from .segment import html_page
from .sl1 import Route, SL1MeleeOnlyGlitchless


def main() -> int:
    output_dir = "docs"

    route_names = set()

    with open(f"{output_dir}/index.html", "w") as index:
        index.write("<h1>Route Index</h1>\n<ul>\n")
        for segment in [
            SL1MeleeOnlyGlitchless(Route.REINFORCED_CLUB),
            SL1MeleeOnlyGlitchless(Route.BATTLE_AXE_PLUS4),
            SL1MeleeOnlyGlitchless(Route.BATTLE_AXE_PLUS4_NO_BLACK_KNIGHT),
            SL1MeleeOnlyGlitchless(Route.BATTLE_AXE_PLUS3),
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
