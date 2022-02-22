from copy import deepcopy
from importlib.resources import open_text as open_text_resource
from itertools import chain
from typing import Iterable, Protocol

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


class Route:
    def __init__(self, *args: Iterable[Action]):
        self.actions: list[Action] = []
        self.add_actions(*args)

    def add_actions(self, *args: Iterable[Action]):
        self.actions.extend(chain(*args))

    def _repr_html_(self):
        state = State()
        region = ""
        html = (
            '<table class="route"><thead>'
            "<tr><th>Souls</th><th>Bank</th><th>HB</th><th>Action</th>"
            "</tr></thead><tbody>"
        )
        for action in self.actions:
            last_state = deepcopy(state)
            action(state)
            state.verify()
            if isinstance(action, Region):
                if action.target != region:
                    html += (
                        '</tbody><tbody><tr><td colspan="4" class="region">'
                        f"{action.target}</td></tr></tbody><tbody>"
                    )
                    region = action.target
            else:
                html += (
                    "<tr>"
                    + _value_cell("souls", last_state.souls, state.souls)
                    + _value_cell("bank", last_state.bank, state.bank)
                    + _value_cell("bones", last_state.bones, state.bones)
                    + '<td class="action">'
                    f'<span class="name">{action.name}</span>'
                    f' <span class="display">{action.display}</span>'
                    f'<br/><span class="detail">{action.detail}'
                    "</span></td></tr>"
                )
        html += "</tbody></table>"
        return html
