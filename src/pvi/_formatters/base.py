from dataclasses import dataclass

from pvi._utils import as_discriminated_union
from pvi.device import Component, Tree


@as_discriminated_union
@dataclass
class Formatter:
    # Screens
    def format_adl(self, components: Tree[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_edl(self, components: Tree[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_opi(self, components: Tree[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_bob(self, components: Tree[Component], basename: str) -> str:
        raise NotImplementedError(self)

    def format_ui(self, components: Tree[Component], basename: str) -> str:
        raise NotImplementedError(self)
