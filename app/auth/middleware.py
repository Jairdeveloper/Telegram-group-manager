from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, List
from app.auth.provider import auth_provider
from app.auth.models import UserRole


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = credentials.credentials
    
    session = auth_provider.verify_session(token)
    if session:
        return {
            "user_id": session.user_id,
            "tenant_id": session.tenant_id,
            "role": session.role.value,
            "type": "session",
            "session_id": session.session_id
        }
    
    api_key = auth_provider.verify_api_key(token)
    if api_key:
        return {
            "tenant_id": api_key.tenant_id,
            "permissions": api_key.permissions,
            "key_id": api_key.key_id,
            "type": "api_key"
        }
    
    raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    if not credentials:
        return None
    
    token = credentials.credentials
    
    session = auth_provider.verify_session(token)
    if session:
        return {
            "user_id": session.user_id,
            "tenant_id": session.tenant_id,
            "role": session.role.value,
            "type": "session"
        }
    
    api_key = auth_provider.verify_api_key(token)
    if api_key:
        return {
            "tenant_id": api_key.tenant_id,
            "permissions": api_key.permissions,
            "key_id": api_key.key_id,
            "type": "api_key"
        }
    
    return None


def require_role(allowed_roles: List[str]):
    async def role_checker(user: Dict = Depends(get_current_user)) -> Dict:
        user_role = user.get("role", "user")
        if user_role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker


def require_permission(permission: str):
    async def permission_checker(user: Dict = Depends(get_current_user)) -> Dict:
        if user.get("type") == "session":
            user_role = user.get("role", "user")
            role_hierarchy = {
                "admin": ["all"],
                "manager": ["read", "write", "chat"],
                "user": ["chat"],
                "api_user": []
            }
            allowed = role_hierarchy.get(user_role, [])
            if "all" not in allowed and permission not in allowed:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        elif user.get("type") == "api_key":
            permissions = user.get("permissions", [])
            if permission not in permissions and "*" not in permissions:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return user
    return permission_checker


def require_tenant_access(tenant_id_param: str = "tenant_id"):
    async def tenant_checker(
        request: Request,
        user: Dict = Depends(get_current_user)
    ) -> Dict:
        path_tenant = request.path_params.get(tenant_id_param)
        user_tenant = user.get("tenant_id")
        
        if user.get("role") != "admin" and path_tenant and path_tenant != user_tenant:
            raise HTTPException(status_code=403, detail="Access denied to this tenant")
        
        return user
    return tenant_checker
