import enum

class UserRole(str, enum.Enum):
    user: str = "user"
    admin: str = "admin"
    super_user: str = "super_user"
