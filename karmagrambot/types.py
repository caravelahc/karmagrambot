from typing import NamedTuple

class UserKarma(NamedTuple):
    name: str
    karma: int

class DevilSaint(NamedTuple):
    devil: UserKarma
    saint: UserKarma
