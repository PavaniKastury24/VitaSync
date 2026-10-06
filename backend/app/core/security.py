from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Dict[str, Any]:
    """
    Validates Supabase-issued JWT from Authorization header.
    In development mode, if no secret or token is configured, provides a mock user payload.
    """
    is_placeholder_secret = not settings.SUPABASE_JWT_SECRET or settings.SUPABASE_JWT_SECRET.startswith("your-")

    if not credentials:
        if settings.ENVIRONMENT == "development" and is_placeholder_secret:
            # Development fallback when Supabase credentials are not yet configured
            return {
                "id": "00000000-0000-0000-0000-000000000001",
                "email": "dev@vitasync.local",
                "role": "authenticated",
                "is_dev_mode": True,
            }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # If Supabase JWT Secret is configured (and not template placeholder), decode and verify signature
    if not is_placeholder_secret:
        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
            user_id: str = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject",
                )
            return {
                "id": user_id,
                "email": payload.get("email"),
                "role": payload.get("role", "authenticated"),
                "is_dev_mode": False,
            }
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(exc)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # In local development without secret, decode unverified for testing
    if settings.ENVIRONMENT == "development":
        try:
            unverified_claims = jwt.get_unverified_claims(token)
            return {
                "id": unverified_claims.get("sub", "dev-user-id"),
                "email": unverified_claims.get("email", "dev@vitasync.local"),
                "role": "authenticated",
                "is_dev_mode": True,
            }
        except Exception:
            return {
                "id": "dev-user-id",
                "email": "dev@vitasync.local",
                "role": "authenticated",
                "is_dev_mode": True,
            }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication secret is unconfigured on server",
    )
