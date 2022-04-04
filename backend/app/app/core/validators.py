import re

# At least one uppercase, lowercase, number, and special character
PASS_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)
# No special characters, between 3 and 20 characters, lowercase, no spaces
USER_REGEX = re.compile(r"^[a-z0-9._-]{3,16}$")

TWOFA_REGEX = re.compile(r"^[0-9]{6}$")


def validate_username(username: str) -> str:
    if not USER_REGEX.match(username):
        raise ValueError(
            "Username must be between 3 and 20 characters, lowercase, no spaces"
        )
    return username


def validate_password(password: str) -> str:
    if not PASS_REGEX.match(password):
        raise ValueError(
            "Password must be at least 8 characters and contain one uppercase, one lowercase, one number, and one special character (@$!%*?&)"
        )
    return password


def validate_twofa(twofa: str) -> str:
    if not TWOFA_REGEX.match(twofa):
        raise ValueError("2FA code must be 6 digits")
    return twofa
