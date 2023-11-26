from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from importlib.resources import open_text as open_text_resource
from typing import Generator, Optional, Protocol, Tuple

from . import styles
from .action import Action, Error, Region, State


class Step(Protocol):
    @property
    def actions(self) -> list[Action]:
        ...

    @property
    def notes(self) -> list[str]:
        ...

    @property
    def condition(self) -> bool:
        ...


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


@dataclass(kw_only=True)
class Segment:  # is a 'Step'
    name: str = ""
    notes: list[str] = field(default_factory=list)
    condition: bool = True
    actions: list[Action] = field(default_factory=list, init=False)

    def __post_init__(self):
        if not self.condition:
            self.notes = []

    def add_steps(self, *steps: Step) -> Segment:
        for step in steps:
            if step.condition:
                self.notes.extend(step.notes)
                self.actions.extend(step.actions)
        return self

    def process(
        self, state: Optional[State] = None
    ) -> Generator[Tuple[State, Action], None, None]:
        if state is None:
            state = State()
        for action in self.actions:
            action(state)
            yield (deepcopy(state), action)
            for error in state.errors():
                yield (deepcopy(state), Error(error))

    def _repr_html_(self, initial_state: Optional[State] = None):
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
        header = '<span class="route_header">'
        if self.name:
            header += f'<span class="route_title">{self.name}</span>'
        if self.notes:
            header += (
                '<ul class="notes">'
                + "".join([f"<li>{note}</li>" for note in self.notes])
                + "</ul>"
            )
        header += "</span>"

        body = (
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
                    body += (
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
                body += (
                    (f'<tr class="{rowclass}">' if rowclass else "<tr>")
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
        body += "</tbody></table>"

        if state.error_count:
            header += (
                f'<span class="error_count">{state.error_count}'
                " errors present.</span>"
            )
        return header + body


def conditional(
    condition: bool, *steps: Step, notes: Optional[list[str]] = None
) -> Segment:
    if not condition:
        return Segment()
    return Segment(notes=notes if notes else []).add_steps(*steps)
