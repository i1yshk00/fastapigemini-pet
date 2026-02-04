from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_PASSWORD_LENGTH = 30


def hash_password(password: str) -> str:
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError("Password is too long")
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    if len(password) > MAX_PASSWORD_LENGTH:
        return False
    return pwd_context.verify(password, hashed)
