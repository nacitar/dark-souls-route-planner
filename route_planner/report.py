from __future__ import annotations
from .route import Enemy, HitType, Segment, DamageTable, Route
from . import styles
from importlib.resources import open_text as open_text_resource
from typing import Optional
from .action import State, Region, Error


def damage_table(
    info: DamageTable,
    *,
    damage_lookup: Optional[dict[str, dict[Enemy, dict[HitType, int]]]],
) -> str:
    if not damage_lookup:
        damage_lookup = {}
    html: list[str] = []
    html.extend(
        [
            f'<span class="route_title">{info.weapon}</span>',
            '<table class="damage"><thead><tr>',
            '<th title="Enemy">Enemy</th>',
            '<th title="Health">Health</th>',
        ]
    )
    for hit_type in info.hit_types:
        html.append(
            f'<th title="{hit_type.info.display_name}">'
            f"{hit_type.info.column_name}</th>"
        )
    html.append("</tr></thead><tbody>")

    for enemy in info.enemies:
        html.extend([f'<tr><td class="enemy">{enemy.info.display_name}</td>'])
        for hit_type in info.hit_types:
            html.append(f'<td class="{hit_type.name.lower()}">')
            damage = (
                damage_lookup.get(info.weapon, {})
                .get(enemy, {})
                .get(hit_type, 0)
            )
            if damage:
                html.append(
                    f"{damage} ({enemy.info.hits(damage=damage)} hits)"
                )
            else:
                html.append("&nbsp;")
            html.append("</td>")
        html.append("</tr>")
    html.append("</tbody></table>")
    return "".join(html)


def page(body: str, *, title: str = "", style: str = "light") -> str:
    if title:
        title = f"<title>{title}</title>"
    if style:
        with open_text_resource(styles, f"{style}.css") as css:
            style = f"<style>{css.read()}</style>"
    return f"<html><head>{title}{style}</head><body>{body}</body></html>"


def _value_cell(name: str, old_value: int, new_value: int) -> str:
    css_class = name.lower().replace(" ", "_")
    html = f'<td class="{css_class}" title="{new_value} {name}">'
    if new_value != old_value:
        change = new_value - old_value
        change_class = "subtract" if change < 0 else "add"
        html += f'<span class="{change_class}">{change:+}</span>'
        html += f"<br/>{new_value}"
    html += "</td>"
    return html


def segment_notes(segment: Segment) -> str:
    if not segment.notes:
        return ""
    return (
        '<ul class="notes">'
        + "".join([f"<li>{note}</li>" for note in segment.notes])
        + "</ul>"
    )


def segment_action_table(
    segment: Segment, *, initial_state: Optional[State] = None
) -> str:
    region_count = 0
    last_state = initial_state if initial_state is not None else State()
    region = ""
    columns = [
        ("Souls", "Souls"),
        ("Item Souls", "☄️"),
        ("Homeward Bones", "🦴"),
        ("Titanite Shards", "🌑"),
        ("Twinkling Titanite", "💎"),
        ("Item Humanities", "👤"),
        ("Humanity", "👨"),
        ("Action", "Action"),
    ]

    html: list[str] = []
    html.append('<table class="route"><thead><tr>')
    html.extend(
        [f'<th title="{column[0]}">{column[1]}</th>' for column in columns]
    )
    html.append("</tr></thead><tbody>")
    for state, action in segment.process(last_state):
        if isinstance(action, Region):
            if action.target != region:
                region_count += 1
                html.append(
                    "</tbody><tbody><tr>"
                    f'<td colspan="{len(columns)}" class="region">'
                    f"{region_count:02}. {action.target}</td></tr>"
                    "</tbody><tbody>"
                )
                region = action.target
        elif action.output:
            rowclass = ""
            if isinstance(action, Error):
                rowclass = "error"
            elif action.optional:
                rowclass = "optional"
            html.append(
                (f'<tr class="{rowclass}">' if rowclass else "<tr>")
                + _value_cell("Souls", last_state.souls, state.souls)
                + _value_cell(
                    "Item Souls", last_state.item_souls, state.item_souls
                )
                + _value_cell("Homeward Bones", last_state.bones, state.bones)
                + _value_cell(
                    "Titanite Shards",
                    last_state.titanite_shards,
                    state.titanite_shards,
                )
                + _value_cell(
                    "Twinkling Titanite",
                    last_state.twinkling_titanite,
                    state.twinkling_titanite,
                )
                + _value_cell(
                    "Item Humanities",
                    last_state.item_humanities,
                    state.item_humanities,
                )
                + _value_cell("Humanity", last_state.humanity, state.humanity)
                + '<td class="action">'
                f'<span class="name">{action.name}</span>'
                f' <span class="display">{action.display}</span>'
                f'<br/><span class="detail">{action.detail}'
                "</span></td></tr>"
            )
        last_state = state
    html.append("</tbody></table>")

    if state.error_count:
        html.insert(  # prepend
            0,
            (
                f'<span class="warning">{state.error_count}'
                " errors present.</span>"
            ),
        )
    return "".join(html)


def route(
    route: Route,
    *,
    damage_tables: Optional[list[DamageTable]] = None,
    damage_lookup: Optional[dict[str, dict[Enemy, dict[HitType, int]]]] = None,
) -> str:
    html: list[str] = []
    html.append('<span class="route_header">')
    if route.name:
        html.append(f'<span class="route_title">{route.name}</span>')
    html.append(segment_notes(route.segment))
    html.append("</span>")

    if route.damage_tables:
        for table in route.damage_tables:
            html.append(damage_table(table, damage_lookup=route.damage_lookup))

    html.append(segment_action_table(route.segment))
    return "".join(html)
