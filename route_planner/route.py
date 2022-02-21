from dataclasses import dataclass
from importlib.resources import open_text as open_text_resource
from os import linesep
from typing import Generator, Iterable, Optional

from . import styles
from .action import Action, Region, State


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


def _numeric_cell(css_class: str, old_value: int, new_value: int) -> str:
    html = f'<td class="{css_class}" title="{new_value}">'
    if new_value != old_value:
        change = new_value - old_value
        change_class = "subtract" if change < 0 else "add"
        html += f'<span class="{change_class}">{change:+}</span>'
        html += f"<br/>{new_value}"
    html += "</td>"
    return html


class Route:
    def __post_init__(self) -> None:
        ...  # keep subclasses from having to redefine __init__'s arguments

    def __init__(self, *, style: str = "") -> None:
        self.actions: list[Action] = []
        self.style: str = style
        self.__post_init__()

    def __str__(self) -> str:
        return type(self).__name__

    def append(self, action_group: Iterable[Action]) -> None:
        for action in action_group:
            self.actions.append(action)

    def extend(self, action_groups: Iterable[Iterable[Action]]) -> None:
        for action_group in action_groups:
            self.append(action_group)

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

    def _repr_html_(self) -> str:
        html = f"<html><head>{linesep}"
        if self.style:
            with open_text_resource(styles, f"{self.style}.css") as css:
                html += f"<style>{linesep}{css.read()}{linesep}</style>"
        html += (
            f"</head><body>{linesep}<h2>{self}</h2>{linesep}"
            + f'<table class="route">{linesep}'
            + "<thead><tr><th>Souls</th><th>Bank</th><th>HB</th>"
            + f"<th>Action</th></tr></thead>{linesep}"
            + f"<tbody>{linesep}"
        )
        last_entry = Entry(Region(""))
        region = ""
        for entry in self.process():
            if isinstance(entry.action, Region):
                if entry.action.target != region:
                    html += (
                        f"</tbody>{linesep}<tbody>{linesep}"
                        + '<tr><td colspan="4" class="region">'
                        + f"{entry.action.target}</td></tr></tbody>{linesep}"
                        + "<tbody>"
                    )
                    region = entry.action.target
            else:

                html += (
                    "<tr>"
                    + _numeric_cell("souls", last_entry.souls, entry.souls)
                    + _numeric_cell("bank", last_entry.bank, entry.bank)
                    + _numeric_cell("bones", last_entry.bones, entry.bones)
                    + '<td class="action">'
                    + f'<span class="name">{entry.action.name}</span>'
                    + f' <span class="display">{entry.action.display}</span>'
                    + "<br/>"
                    + f'<span class="detail">{entry.action.detail}</span>'
                    + "</td>"
                    + f"</tr>{linesep}"
                )
            last_entry = entry
        html += f"</tbody></table>{linesep}</body></html>"
        return html
