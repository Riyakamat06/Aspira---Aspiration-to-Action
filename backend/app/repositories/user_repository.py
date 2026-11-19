"""
user_repository.py  (M1 Database, owner: Ananya)

What it is for:
    All database reads and writes for the "users" table.

Who uses it:
    Riya's auth_service.py (register, login, delete account).

What it contains:
    create_user(db, full_name, email, hashed_password) -> User
    get_user_by_email(db, email) -> User or None
    get_user_by_id(db, user_id) -> User or None
    count_users(db) -> int (used for the 50-user beta cap)
    delete_user(db, user_id) -> True if deleted, False if not found
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User


def create_user(db: Session, full_name: str, email: str, hashed_password: str) -> User:
    """Save a new user. The password must already be hashed."""
    user = User(full_name=full_name, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)  # loads the new id from the database
    return user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Find one user by email (used for login)."""
    return db.scalar(select(User).where(User.email == email))


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Find one user by id."""
    return db.get(User, user_id)


def count_users(db: Session) -> int:
    """How many users exist (used for the 50-user beta cap)."""
    return db.scalar(select(func.count(User.id))) or 0


def delete_user(db: Session, user_id: int) -> bool:
    """Delete the user. The database also deletes their dreams, journal, chat, etc."""
    user = db.get(User, user_id)
    if user is None:
        return False
    db.delete(user)  # ON DELETE CASCADE removes the related rows
    db.commit()
    return True