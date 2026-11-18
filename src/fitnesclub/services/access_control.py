from ..models.admin import Admin
from ..repositories.admins_rep import admins


def require_admin(actor):
    if not isinstance(actor, Admin) or not admins.get_by_id(actor.AdminID):
        raise ValueError("Действие доступно администратору")
