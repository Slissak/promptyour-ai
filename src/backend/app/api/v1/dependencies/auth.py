"""
Authentication dependencies
"""
from fastapi import Depends, HTTPException, status, Query
from typing import Optional
from fastapi.security import OAuth2PasswordBearer
from supabase import create_client, Client
from backend.app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def get_supabase_client() -> Optional[Client]:
    """
    Get Supabase client
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        return None
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

def get_current_user_id(token: str = Depends(oauth2_scheme), supabase: Optional[Client] = Depends(get_supabase_client)) -> str:
    """
    Get current user ID from JWT token using Supabase client.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client is not configured. Cannot authenticate user.",
        )
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user.id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

def get_current_user_id_optional(token: Optional[str] = Depends(oauth2_scheme_optional), supabase: Optional[Client] = Depends(get_supabase_client)) -> str:
    """
    Get current user ID from JWT token, but make it optional.
    If no token is provided, or if the token is invalid, or if supabase is not configured, return a default anonymous user ID.
    """
    if not token or not supabase:
        return "anonymous_user"
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            return "anonymous_user"
        return user.id
    except Exception:
        return "anonymous_user"

def get_current_user_id_from_query(token: str = Query(None), supabase: Optional[Client] = Depends(get_supabase_client)) -> str:
    """
    Get current user ID from JWT token in query parameter.
    """
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase client is not configured. Cannot authenticate user.",
        )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user.id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

def get_current_user_id_from_query_optional(token: Optional[str] = Query(None), supabase: Optional[Client] = Depends(get_supabase_client)) -> str:
    """
    Get current user ID from JWT token in query parameter, but make it optional.
    """
    if not token or not supabase:
        return "anonymous_user"
    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        if not user:
            return "anonymous_user"
        return user.id
    except Exception:
        return "anonymous_user"
