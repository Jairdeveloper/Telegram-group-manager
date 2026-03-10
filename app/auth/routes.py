from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

from app.auth.provider import auth_provider
from app.auth.middleware import get_current_user, require_role
from app.database.repositories import UserRepository, User as RepoUser, ApiKeyModel, get_user_repository


router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str
    tenant_id: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    expires_in: int


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    tenant_id: str
    role: str = "user"


class CreateApiKeyRequest(BaseModel):
    name: str
    permissions: List[str]
    expires_days: Optional[int] = None


class ApiKeyResponse(BaseModel):
    key_id: str
    name: str
    permissions: List[str]
    expires_at: Optional[datetime]
    created_at: datetime


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, user_repo: UserRepository = Depends(get_user_repository)):
    if auth_provider.is_rate_limited(request.username):
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")
    
    auth_provider.set_user_repo(user_repo)
    
    user = auth_provider.authenticate(request.username, request.password, request.tenant_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session_id = auth_provider.create_session(
        user=user,
        ip="0.0.0.0",
        user_agent="api"
    )
    
    return LoginResponse(
        access_token=session_id,
        user_id=user.user_id,
        role=user.role.value if hasattr(user.role, 'value') else user.role,
        expires_in=86400
    )


@router.post("/logout")
async def logout(user: Dict = Depends(get_current_user)):
    session_id = user.get("session_id")
    if session_id:
        auth_provider.revoke_session(session_id)
    return {"message": "Logged out successfully"}


@router.post("/users", response_model=dict)
async def create_user(
    request: CreateUserRequest,
    user: Dict = Depends(require_role(["admin"])),
    user_repo: UserRepository = Depends(get_user_repository)
):
    existing = user_repo.get_by_username(request.username, request.tenant_id)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = auth_provider.hash_password(request.password)
    
    new_user = RepoUser(
        user_id=f"usr_{datetime.utcnow().timestamp()}",
        tenant_id=request.tenant_id,
        email=request.email,
        username=request.username,
        hashed_password=hashed_password,
        role=request.role,
        status="active"
    )
    
    user_repo.save(new_user)
    
    return {
        "user_id": new_user.user_id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }


@router.get("/users/me")
async def get_current_user_info(user: Dict = Depends(get_current_user)):
    return {
        "user_id": user.get("user_id"),
        "tenant_id": user.get("tenant_id"),
        "role": user.get("role"),
        "type": user.get("type")
    }


@router.post("/api-keys", response_model=dict)
async def create_api_key(
    request: CreateApiKeyRequest,
    user: Dict = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    tenant_id = user.get("tenant_id")
    
    auth_provider.set_user_repo(user_repo)
    api_key, key_value = auth_provider.create_api_key(
        tenant_id=tenant_id,
        name=request.name,
        permissions=request.permissions,
        expires_days=request.expires_days
    )
    
    return {
        "key_id": api_key.key_id,
        "key": key_value,
        "name": api_key.name,
        "permissions": api_key.permissions,
        "expires_at": api_key.expires_at
    }


@router.get("/api-keys")
async def list_api_keys(
    user: Dict = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    tenant_id = user.get("tenant_id")
    auth_provider.set_user_repo(user_repo)
    keys = auth_provider.list_api_keys(tenant_id)
    
    return {
        "keys": [
            {
                "key_id": k.key_id,
                "name": k.name,
                "permissions": k.permissions,
                "expires_at": k.expires_at,
                "last_used": k.last_used
            }
            for k in keys
        ]
    }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    user: Dict = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    tenant_id = user.get("tenant_id")
    auth_provider.set_user_repo(user_repo)
    
    if auth_provider.revoke_api_key(key_id, tenant_id):
        return {"message": "API key revoked"}
    raise HTTPException(status_code=404, detail="API key not found")


@router.post("/refresh")
async def refresh_token(user: Dict = Depends(get_current_user)):
    session_id = user.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="No session to refresh")
    
    new_session_id = auth_provider.refresh_session(session_id)
    if not new_session_id:
        raise HTTPException(status_code=401, detail="Session expired")
    
    return {
        "access_token": new_session_id,
        "token_type": "bearer",
        "expires_in": 86400
    }
