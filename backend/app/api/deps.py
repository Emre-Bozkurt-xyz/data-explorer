from fastapi import Header, HTTPException, status


def get_current_user_id(x_user_id: str = Header(alias="X-User-Id")) -> str:
    """
    MVP 'auth': require X-User-Id header for any bookmark operations.
    """
    user_id = x_user_id.strip()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-Id header is required",
        )
    return user_id
