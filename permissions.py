TOKENS = {
    "reader-token": {
        "user": "order-reader",
        "scopes": ["orders:read"],
    },
    "operator-token": {
        "user": "order-operator",
        "scopes": ["orders:read", "orders:write"],
    },
    "admin-token": {
        "user": "order-admin",
        "scopes": ["orders:read", "orders:write", "orders:cancel"],
    },
}


def get_identity(token: str) -> dict:
    identity = TOKENS.get(token)
    if not identity:
        raise PermissionError("Invalid API token")
    return identity


def require_scope(token: str, required_scope: str) -> dict:
    identity = get_identity(token)
    if required_scope not in identity["scopes"]:
        raise PermissionError(
            f"Permission denied. Required scope: {required_scope}"
        )
    return identity
