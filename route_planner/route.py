from dataclasses import dataclass
from typing import Generator, Iterable, Optional

from .event import Event, Region, State


@dataclass(frozen=True)
class Entry:
    souls: int
    item_souls: int
    bones: int
    event: Event

    def validate(self):
        error: str = ""
        if self.souls < 0:
            error += f" souls({self.souls})"
        if self.item_souls < 0:
            error += f" item_souls({self.item_souls})"
        if self.bones < 0:
            error += f" bones({self.bones})"
        if error:
            raise RuntimeError(f"insufficent amount:{error}")


class Route:
    def __init__(self, *, state: Optional[State] = None):
        if state is None:
            state = State()
        self.state = state
        self.output: list[Entry] = []
        if self.state.region:
            self.append([Region(self.state.region)])

    def append(self, event_group: Iterable[Event]):
        for event in event_group:
            event(self.state)
            self.output.append(
                Entry(
                    souls=self.state.souls,
                    item_souls=self.state.item_souls,
                    bones=self.state.items["Homeward Bone"],
                    event=event,
                )
            )

    def extend(self, event_groups: Iterable[Iterable[Event]]):
        for event_group in event_groups:
            self.append(event_group)

    def process(self) -> Generator[Entry, None, None]:
        for entry in self.output:
            entry.validate()
            yield entry
