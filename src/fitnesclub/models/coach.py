from dataclasses import dataclass


@dataclass
class Coach:
    CoachID: int
    name: str
    specialization: str | None
    email: str
