from dataclasses import dataclass, field


@dataclass
class Admin:
    AdminID: int
    name: str
    login: str
    password_hash: str = field(repr=False)
    email: str
