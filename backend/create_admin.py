"""Interactively create the first administrator account."""

import getpass
import re

from app.core.security import hash_password
from app.db.session import Sessionlocal
from app.models.enums import Role
from app.models.user import User

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def main() -> int:
    full_name = input("Administrator name: ").strip()
    email = input("Administrator email: ").strip().lower()
    password = getpass.getpass("Password (8-72 UTF-8 bytes): ")
    confirmation = getpass.getpass("Confirm password: ")

    if len(full_name) < 2 or len(full_name) > 100:
        print("Name must be between 2 and 100 characters.")
        return 1
    if not EMAIL_RE.fullmatch(email):
        print("Enter a valid email address.")
        return 1
    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        print("Password must be at least 8 characters and no more than 72 UTF-8 bytes.")
        return 1
    if password != confirmation:
        print("Passwords do not match.")
        return 1

    db = Sessionlocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print("An account with this email already exists.")
            return 1
        db.add(
            User(
                full_name=full_name,
                email=email,
                password_hash=hash_password(password),
                role=Role.admin,
            )
        )
        db.commit()
    finally:
        db.close()

    print(f"Administrator account created for {email}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
