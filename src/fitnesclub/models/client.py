from dataclasses import dataclass, field


@dataclass
class Client:
    ClientID: int
    name: str
    phone_number: str
    password_hash: str = field(repr=False)
    email: str
    AdminID: int
