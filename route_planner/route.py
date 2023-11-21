from __future__ import annotations

from copy import deepcopy
from importlib.resources import open_text as open_text_resource
from typing import Generator, Iterable, Optional, Protocol, Tuple

from . import styles
from .action import Action, Region, State


class HtmlSource(Protocol):
    def _repr_html_(self) -> str:
        ...


def html(source: HtmlSource) -> str:
    return source._repr_html_()


def html_page(source: HtmlSource, *, title: str = "", style: str = "light"):
    if title:
        title = f"<title>{title}</title>"
    if style:
        with open_text_resource(styles, f"{style}.css") as css:
            style = f"<style>{css.read()}</style>"
    body = html(source)
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


class Segment:
    def __init__(self, *actions: Action, notes: list[str] = []):
        self.notes = notes
        self.actions: list[Action] = []
        for action in actions:
            self.actions.append(action)

    def append(self, other: Segment):
        self.actions.extend(other.actions)
        self.notes.extend(other.notes)

    def extend(self, others: Iterable[Segment]):
        for other in others:
            self.append(other)

    def process(
        self, state: Optional[State] = None
    ) -> Generator[Tuple[State, Action], None, None]:
        if state is None:
            state = State()
        for action in self.actions:
            if action.enabled:
                action(state)
                state.verify()
                yield (deepcopy(state), action)

    def _repr_html_(self):
        region_count = 0
        last_state = State()
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
        html = (
            '<table class="route"><thead><tr>'
            + "".join(
                f'<th title="{column[0]}">{column[1]}</th>'
                for column in columns
            )
            + "</tr></thead><tbody>"
        )
        for state, action in self.process(last_state):
            if isinstance(action, Region):
                if action.target != region:
                    region_count += 1
                    html += (
                        "</tbody><tbody><tr>"
                        f'<td colspan="{len(columns)}" class="region">'
                        f"{region_count:02}. {action.target}</td></tr>"
                        "</tbody><tbody>"
                    )
                    region = action.target
            elif action.output:
                html += (
                    ('<tr class="optional">' if action.optional else "<tr>")
                    + _value_cell("Souls", last_state.souls, state.souls)
                    + _value_cell(
                        "Item Souls", last_state.item_souls, state.item_souls
                    )
                    + _value_cell(
                        "Homeward Bones", last_state.bones, state.bones
                    )
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
                    + _value_cell(
                        "Humanity", last_state.humanity, state.humanity
                    )
                    + '<td class="action">'
                    f'<span class="name">{action.name}</span>'
                    f' <span class="display">{action.display}</span>'
                    f'<br/><span class="detail">{action.detail}'
                    "</span></td></tr>"
                )
            last_state = state
        html += "</tbody></table>"
        return html


class Route(Segment):
    def __init__(
        self, *actions: Action, notes: list[str] = [], name: str = ""
    ):
        super().__init__(*actions, notes=notes)
        self.name = name

    def _repr_html_(self):
        html = '<span class="route_header">'
        if self.name:
            html += f'<span class="route_title">{self.name}</span>'
        if self.notes:
            html += (
                '<ul class="notes">'
                + "".join([f"<li>{note}</li>" for note in self.notes])
                + "</ul>"
            )
        html += "</span>"
        return html + super()._repr_html_()
