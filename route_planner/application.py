from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from . import report
from .route import Route

CURRENT_FILE_DIRECTORY = Path(__file__).resolve().parent


class RouteExporter(Protocol):
    EXPORTED_ROUTES: list[Route]


def sanitize_filename(value: str) -> str:
    return "".join(ch for ch in value if ch.isalnum())


def load_routes() -> list[Route]:
    routes_subdirectory = Path("routes")
    routes: list[Route] = []
    files: list[Path] = [
        entry
        for entry in (CURRENT_FILE_DIRECTORY / routes_subdirectory).iterdir()
        if entry.is_file()
        and entry.suffix.lower() == ".py"
        and not entry.stem.startswith("_")
    ]
    for file in files:
        module_name = (
            f"{__package__}.{'.'.join(routes_subdirectory.parts)}.{file.stem}"
        )
        spec = importlib.util.spec_from_file_location(module_name, file)
        if not spec:
            raise RuntimeError(f"No spec could be loaded for {file}")
        module = importlib.util.module_from_spec(spec)
        if not module:
            raise RuntimeError(f"No module could be loaded for {file}")
        if not spec.loader:
            raise RuntimeError(f"Spec has no loader for {file}")
        sys.modules[module_name] = module  # so dataclasses and such are happy
        spec.loader.exec_module(module)
        if (
            not hasattr(module, "EXPORTED_ROUTES")
            or not module.EXPORTED_ROUTES
        ):
            raise RuntimeError(
                f"Module does not contain any exported routes: {file}"
            )
        route_exporter = cast(RouteExporter, module)
        routes.extend(route_exporter.EXPORTED_ROUTES)
    route_names: set[str] = set()
    for route in routes:
        if route.name in route_names:
            raise RuntimeError(
                f"Multiple routes with the same name: {route.name}"
            )
        route_names.add(route.name)
    routes.sort(key=lambda route: route.name)
    return routes


def main() -> int:
    output_directory = CURRENT_FILE_DIRECTORY.parent / "docs"
    # TODO: create dir if needed, delete contents otherwise
    routes = load_routes()
    with open(f"{output_directory}/index.html", "w") as index:
        index.write("<h1>Route Index</h1><ul>")
        for route in routes:
            filename = f"{sanitize_filename(route.name)}.html"
            with open(f"{output_directory}/{filename}", "w") as route_file:
                route_file.write(
                    report.page(report.route(route), title=route.name)
                )
            index.write(f'<li><a href="{filename}">{route.name}</a></li>\n')
        index.write("</ul>")
    return 0
