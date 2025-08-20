
import bcrypt

def hash_pin(pin: str) -> str:
    if not pin or not pin.isdigit() or len(pin) < 4:
        raise ValueError("PIN must be at least 4 digits.")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pin.encode(), salt).decode()

def verify_pin(pin: str, hashed: str) -> bool:
    return bcrypt.checkpw(pin.encode(), hashed.encode())
