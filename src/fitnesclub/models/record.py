from dataclasses import dataclass


@dataclass
class Record:
    RecordID: int
    time: str
    date: str
    status: str
    ClientID: int
    AdminID: int
    CoachID: int
