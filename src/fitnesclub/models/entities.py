from dataclasses import dataclass, field


@dataclass
class Admin:
    AdminID: int
    name: str
    login: str
    password_hash: str = field(repr=False)
    email: str


@dataclass
class Client:
    ClientID: int
    name: str
    phone_number: str
    password_hash: str = field(repr=False)
    email: str
    AdminID: int


@dataclass
class Coach:
    CoachID: int
    name: str
    specialization: str | None
    email: str


@dataclass
class Record:
    RecordID: int
    time: str
    date: str
    status: str
    ClientID: int
    AdminID: int
    CoachID: int

