import re
from fastapi import HTTPException

# Mock database simulating user access levels for specific homes
MOCK_USER_HOMES = {
    "test@example.com": ["home_123", "home_456"],
    "admin@example.com": ["home_123", "home_456", "home_789"]
}

# Only allow letters, digits, underscores, and hyphens in home IDs
_HOME_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]+$')

def validate_home_access(user_id: str, home_id: str):
    """
    Validates the home ID format and checks if the user has access.
    Rejects inputs containing special characters.
    """
    if not _HOME_ID_PATTERN.match(home_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid Home ID: special characters are not allowed. "
                   "Only letters, digits, underscores, and hyphens are permitted."
        )

    if not home_id.startswith("home_"):
        raise HTTPException(
            status_code=400,
            detail="Invalid Home ID format. Must start with 'home_'"
        )

    # Permission check (mock database)
    if user_id in MOCK_USER_HOMES:
        if home_id not in MOCK_USER_HOMES[user_id]:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: User does not have access to home '{home_id}'"
            )
