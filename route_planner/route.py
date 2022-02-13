from dataclasses import dataclass
from typing import Generator, Iterable, Optional

from .action import Action, Region, State


@dataclass(frozen=True)
class Entry:
    action: Action
    souls: int = 0
    bank: int = 0
    bones: int = 0

    def validate(self) -> None:
        error: str = ""
        if self.souls < 0:
            error += f" souls({self.souls})"
        if self.bank < 0:
            error += f" bank({self.bank})"
        if self.bones < 0:
            error += f" bones({self.bones})"
        if error:
            raise RuntimeError(f"insufficent amount:{error}")

    def _repr_html_(self) -> str:
        return (
            "<tr>"
            f'<td class="souls">{self.souls}</td>'
            f'<td class="bank">{self.bank}</td>'
            f'<td class="bones">{self.bones}</td>'
            f'<td class="action">'
            f'<span class="name">{self.action.name}</span>'
            f' <span class="target">{self.action.target}</span><br/>'
            f'<span class="detail">{self.action.detail}</span>'
            "</td>"
            "</tr>"
        )


class Route:
    def __init__(self):
        self.actions: list[Action] = []

    def append(self, action_group: Iterable[Action]):
        for action in action_group:
            self.actions.append(action)

    def extend(self, action_groups: Iterable[Iterable[Action]]):
        for action_group in action_groups:
            self.append(action_group)

    def process(
        self, state: Optional[State] = None
    ) -> Generator[Entry, None, None]:
        if state is None:
            state = State()
        for action in self.actions:
            action(state)
            entry = Entry(
                souls=state.souls,
                bank=state.bank,
                bones=state.items["Homeward Bone"],
                action=action,
            )
            entry.validate()
            yield entry

    def _repr_html_(self) -> str:
        html_parts = []

        html_parts.append(
            "<style>"
            "table.route {"
            "   border: 1px solid Black;"
            "}"
            "table.route th {"
            "   border: 1px solid Black;"
            "   text-align: center;"
            "   background-color: LightSkyBlue;"
            "}"
            "table.route td,"
            "table.route th {"
            "   font-size: medium;"
            "   padding-left: 0.5em;"
            "   padding-right: 0.5em;"
            "   padding-top: 0.1em;"
            "   padding-bottom: 0.1em;"
            "   border-left: 1px solid Black;"
            "   border-right: 1px solid Black;"
            "}"
            "table.route td.region {"
            "   background-color: LightGray;"
            "   border-top: 1px solid Black;"
            "   border-bottom: 1px solid Black;"
            "   text-align: center;"
            "   font-size: large;"
            "   font-weight: bold;"
            "}"
            "table.route td {"
            "   border-top: 1px solid DarkGray;"
            "}"
            "table.route td.action {"
            "   text-align: left;"
            "}"
            "table.route td.action span.name {"
            "   font-weight: bold;"
            "}"
            "table.route td.souls,"
            "table.route td.bank,"
            "table.route td.bones {"
            "   text-align: center;"
            "}"
            "table.route span.add,"
            "table.route span.subtract,"
            "table.route span.detail {"
            "   font-size: small;"
            "}"
            "table.route span.add {"
            "   color: DarkGreen;"
            "   font-weight: bold;"
            "}"
            "table.route span.subtract {"
            "   color: Red;"
            "   font-weight: bold;"
            "}"
            "table.route span.detail {"
            "   color: DarkBlue;"
            "}"
            "</style>"
        )

        html_parts.append(
            '<table class="route">'
            "<thead><tr><th>Souls</th><th>Bank</th><th>HB</th>"
            "<th>Action</th></tr></thead>"
        )
        last_entry = Entry(Region(""))
        region = ""
        for entry in self.process():

            def numeric_cell(old_value: int, new_value: int) -> str:
                if new_value != old_value:
                    delta = new_value - old_value
                    css_class = "subtract" if delta < 0 else "add"
                    extra = (
                        f'<span class="{css_class}">'
                        f"{new_value - old_value:+}</span><br/>"
                    )
                    return f"{extra}{new_value}"
                else:
                    return ""

            if isinstance(entry.action, Region):
                if entry.action.target != region:
                    html_parts.append(
                        '<tr><td colspan="4" class="region">'
                        f"{entry.action.target}</td></tr>"
                    )
                    region = entry.action.target
            else:
                souls_cell = numeric_cell(last_entry.souls, entry.souls)
                bank_cell = numeric_cell(last_entry.bank, entry.bank)
                bones_cell = numeric_cell(last_entry.bones, entry.bones)
                html_parts.append(
                    "<tr>"
                    f'<td class="souls">{souls_cell}</td>'
                    f'<td class="bank">{bank_cell}</td>'
                    f'<td class="bones">{bones_cell}</td>'
                    f'<td class="action">'
                    f'<span class="name" style="color: red">{entry.action.name}</span>'
                    f' <span class="target">{entry.action.display}</span><br/>'
                    f'<span class="detail">{entry.action.detail}</span>'
                    "</td>"
                    "</tr>"
                )
            last_entry = entry
        html_parts.append("</table>")
        return "".join(html_parts)
