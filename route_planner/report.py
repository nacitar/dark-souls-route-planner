from __future__ import annotations

from html.parser import HTMLParser
from importlib.resources import open_text as open_text_resource
from math import ceil
from os import linesep
from typing import Optional

from . import styles
from .action import Error, State
from .route import DamageTable, Enemy, Hit, HitType, Route, Segment


# TODO: something better than string appending for the pretty html
class ConvertMinifiedToPrettyHtmlParser(HTMLParser):
    SINGLE_LINE_TAGS = ["tr", "li", "span", "title"]
    EMPTY_TAGS = ["br"]

    def __init__(self) -> None:
        super().__init__()
        self.indent_level: int = 0
        self.inside_single_line_tag: list[str] = []
        self._pretty_html_parts: list[str] = []

    def __indent_str(self) -> str:
        return "    " * self.indent_level

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, Optional[str]]]
    ) -> None:
        attrs_str = "".join(
            f' {name}="{value}"' if value is not None else f" {name}"
            for name, value in attrs
        )
        if self.inside_single_line_tag:
            self._pretty_html_parts.append(f"<{tag}{attrs_str}")
        else:
            self._pretty_html_parts.append(
                linesep + self.__indent_str() + f"<{tag}{attrs_str}"
            )
        if tag in ConvertMinifiedToPrettyHtmlParser.SINGLE_LINE_TAGS:
            self.inside_single_line_tag.append(tag)
        if tag not in ConvertMinifiedToPrettyHtmlParser.EMPTY_TAGS:
            self._pretty_html_parts.append(">")  # terminate normally
            self.indent_level += 1
        else:
            self._pretty_html_parts.append("/>")  # self-close empty tags

    def handle_endtag(self, tag: str) -> None:
        if tag in ConvertMinifiedToPrettyHtmlParser.EMPTY_TAGS:
            return  # empty tags self-close in handle_starttag
        self.indent_level -= 1
        if self.inside_single_line_tag:
            self._pretty_html_parts.append(f"</{tag}>")
            if tag == self.inside_single_line_tag[-1]:
                self.inside_single_line_tag.pop()
        else:
            self._pretty_html_parts.append(
                linesep + self.__indent_str() + f"</{tag}>"
            )

    def handle_data(self, data: str) -> None:
        if self.inside_single_line_tag:
            self._pretty_html_parts.append(data)
        else:
            for line in data.splitlines():
                self._pretty_html_parts.append(
                    linesep + self.__indent_str() + line
                )

    def pretty_html(self) -> str:
        return "".join(self._pretty_html_parts)


def convert_minified_to_pretty_html(content: str) -> str:
    parser = ConvertMinifiedToPrettyHtmlParser()
    parser.feed(content)
    return parser.pretty_html()


def page(body: str, *, title: str = "", style: str = "light") -> str:
    if title:
        title = f"<title>{title}</title>"
    if style:
        with open_text_resource(styles, f"{style}.css") as css:
            style = f"<style>{css.read()}</style>"
    content = f"<html><head>{title}{style}</head><body>{body}</body></html>"
    return convert_minified_to_pretty_html(content)


def damage_table(
    table: DamageTable,
    *,
    hit_lookup: Optional[dict[str, dict[Enemy, dict[HitType, Hit]]]],
) -> str:
    if not hit_lookup:
        hit_lookup = {}
    html: list[str] = []
    html.append('<table class="route"><thead><tr>')
    for hit_type in table.hit_types:
        html.append(
            f'<th colspan="2" title="{hit_type.info.display_name}">'
            f"{hit_type.info.column_name}</th>"
        )
    html.append('<th title="Enemy">Enemy</th></tr></thead><tbody>')

    for enemy in table.enemies:
        for form_name, health in enemy.info.form_health_lookup.items():
            html.append("<tr>")
            for hit_type in table.hit_types:
                hit: Hit = (
                    hit_lookup.get(table.weapon, {})
                    .get(enemy, {})
                    .get(hit_type, Hit())
                )
                td_classes: list[str] = [hit_type.name.lower()]
                hit_display = hit_type.info.display_name.lower()
                hit_cells: list[tuple[int, str, list[str]]] = [
                    (hit.damage, "hits", []),
                    (hit.with_rtsr, "hits with RTSR", ["rtsr"]),
                ]
                for damage, hit_text, extra_classes in hit_cells:
                    html.append(  # partial tag
                        f'<td class="{" ".join(td_classes + extra_classes)}"'
                    )
                    if damage:
                        hits = ceil(health / damage)
                        title = f"{hits} {hit_display} {hit_text} for {damage}"
                        html.append(
                            f' title="{title}">{hits}</td>'
                        )  # rest of tag
                    else:
                        html.append("></td>")  # rest of tag
            html.append(
                f'<td class="enemy" title="{health} total hp">'
                f"{form_name}</td></tr>"
            )
    html.append("</tbody></table>")
    return "".join(html)


def segment_notes(segment: Segment) -> str:
    if not segment.notes:
        return ""
    return (
        '<ul class="route notes">'
        + "".join([f"<li>{note}</li>" for note in segment.notes])
        + "</ul>"
    )


def _value_cell(name: str, old_value: int, new_value: int) -> str:
    css_class = name.lower().replace(" ", "_")
    html = f'<td class="{css_class}" title="{new_value} {name.lower()}">'
    if new_value != old_value:
        change = new_value - old_value
        change_class = "subtract" if change < 0 else "add"
        html += f'<span class="{change_class}">{change:+}</span>'
        html += f"<br/>{new_value}"
    html += "</td>"
    return html


def segment_steps_table(
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
        if action.output:
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
        if state.region != region:
            region = state.region
            region_count += 1
            html.append(
                "</tbody><tbody><tr>"
                f'<td colspan="{len(columns)}" class="region">'
                f"{region_count:02}. {region}</td></tr>"
                "</tbody><tbody>"
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
    hit_lookup: Optional[dict[str, dict[Enemy, dict[HitType, Hit]]]] = None,
) -> str:
    html: list[str] = []
    if route.name:
        html.append(f'<span class="route display_name">{route.name}</span>')
    notes = segment_notes(route.segment)
    if notes:
        html.append('<span class="route section">Notes</span>')
        html.append(segment_notes(route.segment))
    if route.damage_tables:
        for table in route.damage_tables:
            html.append(
                f'<span class="route section">Hits ({table.weapon})</span>'
            )
            html.append(damage_table(table, hit_lookup=route.hit_lookup))
    html.append('<span class="route section">Steps</span>')
    html.append(segment_steps_table(route.segment))
    return "".join(html)
