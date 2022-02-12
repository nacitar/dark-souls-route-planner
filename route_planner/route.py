from dataclasses import dataclass
from typing import Generator, Iterable, Optional

from .action import Action, Region, State


@dataclass(frozen=True)
class Entry:
    souls: int
    bank: int
    bones: int
    action: Action

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
                "<tr>",
                '<td class="souls">{souls}</td>',
                '<td class="bank">{bank}</td>',
                '<td class="bones">{bones}</td>',
                '<td class="action">{action}</td>',
                '</tr>'
                )
        #return f'<span style="font-family:Courier; color:Blue; font-size: 20px;">{self.souls}</span>'


class Route:
    def __init__(self, *, state: Optional[State] = None):
        if state is None:
            state = State()
        self.state = state
        self.output: list[Entry] = []
        if self.state.region:
            self.append([Region(self.state.region)])

    def append(self, action_group: Iterable[Action]):
        for action in action_group:
            action(self.state)
            self.output.append(
                Entry(
                    souls=self.state.souls,
                    bank=self.state.bank,
                    bones=self.state.items["Homeward Bone"],
                    action=action,
                )
            )

    def extend(self, action_groups: Iterable[Iterable[Action]]):
        for action_group in action_groups:
            self.append(action_group)

    def process(self) -> Generator[Entry, None, None]:
        for entry in self.output:
            entry.validate()
            yield entry
