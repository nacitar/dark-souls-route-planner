from dataclasses import dataclass, field
from importlib.resources import open_text as open_text_resource
from typing import Generator, Iterable, Optional, Protocol

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


def _value_cell(css_class: str, old_value: int, new_value: int) -> str:
    html = f'<td class="{css_class}" title="{new_value}">'
    if new_value != old_value:
        change = new_value - old_value
        change_class = "subtract" if change < 0 else "add"
        html += f'<span class="{change_class}">{change:+}</span>'
        html += f"<br/>{new_value}"
    html += "</td>"
    return html


@dataclass(frozen=True)
class Entry:
    action: Action
    souls: int = 0
    bank: int = 0
    bones: int = 0

    def __post_init__(self) -> None:
        error: str = ""
        if self.souls < 0:
            error += f" souls({self.souls})"
        if self.bank < 0:
            error += f" bank({self.bank})"
        if self.bones < 0:
            error += f" bones({self.bones})"
        if error:
            raise RuntimeError(
                f"insufficent amount:{error} after {self.action}"
            )


@dataclass
class Segment:
    actions: list[Action] = field(default_factory=list)

    def __str__(self) -> str:
        return type(self).__name__

    def add_actions(self, *args: Action):
        self.actions.extend(args)

    def process(
        self, state: Optional[State] = None
    ) -> Generator[Entry, None, None]:
        if state is None:
            state = State()
        for action in self.actions:
            action(state)

            overused: dict[str, int] = {
                key: value for key, value in state.items.items() if value < 0
            }
            if overused:
                raise RuntimeError(
                    f'insufficient items: {", ".join(overused.keys())}'
                )
            yield Entry(
                souls=state.souls,
                bank=state.bank,
                bones=state.items["Homeward Bone"],
                action=action,
            )


@dataclass
class Route:
    segments: list[Segment] = field(default_factory=list)

    def add_segments(self, *args: Segment):
        self.segments.extend(args)

    def _repr_html_(self):
        last_entry = Entry(Region(""))
        region = ""
        state = State()
        html = ""
        for segment in self.segments:
            html += (
                f'<span class="segment_name">{segment}</span>'
                '<table class="segment"><thead>'
                "<tr><th>Souls</th><th>Bank</th><th>HB</th><th>Action</th>"
                "</tr></thead><tbody>"
            )
            for entry in segment.process(state):
                if isinstance(entry.action, Region):
                    if entry.action.target != region:
                        html += (
                            "</tbody><tbody>"
                            '<tr><td colspan="4" class="region">'
                            f"{entry.action.target}</td></tr>"
                            "</tbody><tbody>"
                        )
                        region = entry.action.target
                else:
                    html += (
                        "<tr>"
                        + _value_cell("souls", last_entry.souls, entry.souls)
                        + _value_cell("bank", last_entry.bank, entry.bank)
                        + _value_cell("bones", last_entry.bones, entry.bones)
                        + '<td class="action">'
                        f'<span class="name">{entry.action.name}</span>'
                        f' <span class="display">{entry.action.display}</span>'
                        f'<br/><span class="detail">{entry.action.detail}'
                        "</span></td></tr>"
                    )
                last_entry = entry
            html += "</tbody></table>"
        return html
