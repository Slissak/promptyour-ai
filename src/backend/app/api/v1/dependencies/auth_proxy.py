from fastapi import Header, HTTPException, status, Depends
from typing import Optional
from backend.app.core.config import settings
from backend.app.db.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.database import get_db_session
from sqlalchemy.future import select
import uuid

# Dependency to get trusted headers from the Edge Function
async def get_auth_headers(
    x_user_id: str = Header(..., description="User ID from Supabase Edge Function"),
    x_user_email: str = Header(..., description="User email from Supabase Edge Function"),
    x_role: Optional[str] = Header("user", description="User role from Supabase Edge Function"),
    x_api_key: str = Header(..., description="Shared secret from Supabase Edge Function")
) -> dict:
    # Validate the shared secret key
    if x_api_key != settings.BACKEND_API_KEY: # Assuming BACKEND_API_KEY is defined in settings
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal API key",
        )
    
    # Ensure user_id is a valid UUID
    try:
        uuid.UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid x-user-id format",
        )

    return {
        "user_id": x_user_id,
        "user_email": x_user_email,
        "user_role": x_role,
        "is_authenticated": True
    }

# This will replace the old get_current_user dependency
async def get_current_user_from_proxy(
    auth_headers: dict = Depends(get_auth_headers),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    user_id = auth_headers["user_id"]
    # Fetch user from your database based on the trusted x-user-id
    # You might want to create the user here if they don't exist yet (lazy registration)
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalars().first()

    if not user:
        # User not found in our DB, potentially a new user from Supabase Auth
        # Create a new user entry in our DB
        user = User(
            id=uuid.UUID(user_id),
            email=auth_headers["user_email"],
            # Assuming 'full_name' can be derived or is optional
            full_name=auth_headers["user_email"].split('@')[0], 
            # Default password_hash should be null for Supabase Auth users
            password_hash=None, 
            is_active=True,
            is_superuser=(auth_headers["user_role"] == "admin") # Set superuser based on role
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    return user

# This will replace the old get_current_user_id_optional dependency
async def get_current_user_id_from_proxy_optional(
    auth_headers: Optional[dict] = Depends(get_auth_headers)
) -> str:
    # If auth_headers are present, return the user_id
    if auth_headers:
        return auth_headers["user_id"]
    # Otherwise, return "anonymous_user" (no trusted headers, means unauthenticated)
    return "anonymous_user"
