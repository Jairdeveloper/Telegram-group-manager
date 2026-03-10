"""Enterprise API routes for multi-tenant access."""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, Optional
from pydantic import BaseModel

from app.auth.middleware import get_current_user
from app.billing import get_billing_service
from app.audit import get_audit_service, AuditEventType
from app.monitoring import get_metrics_service
from app.database.repositories import ConversationRepository, get_conversation_repository


router = APIRouter(prefix="/api/v1", tags=["enterprise"])


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    metadata: Optional[dict] = None


class HistoryResponse(BaseModel):
    session_id: str
    messages: list


async def get_client_info(request: Request) -> Dict[str, str]:
    """Extract client information from request."""
    return {
        "ip_address": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown")
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    request: Request,
    user: Dict = Depends(get_current_user),
    billing_service=Depends(get_billing_service),
    audit_service=Depends(get_audit_service),
    metrics_service=Depends(get_metrics_service),
    conversation_repo: ConversationRepository = Depends(get_conversation_repository)
):
    """Send a chat message."""
    import time
    start_time = time.time()
    
    tenant_id = user.get("tenant_id")
    user_id = user.get("user_id")
    user_type = user.get("type", "user")
    
    allowed, msg = billing_service.check_limit(tenant_id, "requests")
    if not allowed:
        metrics_service.record_error("rate_limit", "/api/v1/chat")
        raise HTTPException(429, detail=msg)
    
    client_info = await get_client_info(request)
    
    try:
        response = await process_message(
            tenant_id=tenant_id,
            session_id=chat_request.session_id,
            message=chat_request.message
        )
        
        conversation_repo.save_message(
            tenant_id=tenant_id,
            session_id=chat_request.session_id,
            user_message=chat_request.message,
            bot_response=response.get("text", ""),
            metadata=response.get("metadata", {})
        )
        
        billing_service.track_usage(tenant_id, requests=1, tokens=response.get("tokens", 0))
        
        latency = time.time() - start_time
        metrics_service.record_request(tenant_id, "/api/v1/chat", 200)
        metrics_service.record_latency(tenant_id, "/api/v1/chat", latency)
        
        if response.get("tokens", 0) > 0:
            metrics_service.record_tokens(
                tenant_id, 
                response.get("model", "unknown"),
                response.get("tokens", 0)
            )
        
        audit_service.log(
            tenant_id=tenant_id,
            event_type=AuditEventType.CHAT_MESSAGE,
            actor_id=user_id or user.get("key_id"),
            actor_type=user_type,
            resource_type="session",
            resource_id=chat_request.session_id,
            action="send_message",
            ip_address=client_info.get("ip_address"),
            user_agent=client_info.get("user_agent")
        )
        
        return ChatResponse(
            session_id=chat_request.session_id,
            response=response.get("text", ""),
            metadata=response.get("metadata", {})
        )
        
    except Exception as e:
        latency = time.time() - start_time
        metrics_service.record_request(tenant_id, "/api/v1/chat", 500)
        metrics_service.record_latency(tenant_id, "/api/v1/chat", latency)
        metrics_service.record_error("internal_error", "/api/v1/chat")
        
        audit_service.log(
            tenant_id=tenant_id,
            event_type=AuditEventType.CHAT_MESSAGE,
            actor_id=user_id or user.get("key_id"),
            actor_type=user_type,
            resource_type="session",
            resource_id=chat_request.session_id,
            action="send_message",
            result="failure",
            ip_address=client_info.get("ip_address"),
            metadata={"error": str(e)}
        )
        
        raise HTTPException(500, detail="Internal server error")


async def process_message(tenant_id: str, session_id: str, message: str) -> dict:
    """Process chat message. Placeholder for actual implementation."""
    return {
        "text": f"Echo: {message}",
        "tokens": len(message.split()),
        "model": "gpt-4",
        "metadata": {}
    }


@router.get("/history/{session_id}", response_model=HistoryResponse)
async def history(
    session_id: str,
    limit: int = 50,
    user: Dict = Depends(get_current_user),
    conversation_repo: ConversationRepository = Depends(get_conversation_repository)
):
    """Get conversation history for a session."""
    tenant_id = user.get("tenant_id")
    
    messages = conversation_repo.get_history(tenant_id, session_id, limit)
    
    return HistoryResponse(
        session_id=session_id,
        messages=messages
    )


@router.get("/sessions")
async def list_sessions(
    user: Dict = Depends(get_current_user),
    conversation_repo: ConversationRepository = Depends(get_conversation_repository)
):
    """List all sessions for the tenant."""
    tenant_id = user.get("tenant_id")
    
    sessions = conversation_repo.get_sessions(tenant_id)
    
    return {
        "sessions": sessions,
        "count": len(sessions)
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user: Dict = Depends(get_current_user),
    audit_service=Depends(get_audit_service),
    conversation_repo: ConversationRepository = Depends(get_conversation_repository)
):
    """Delete a session and its history."""
    tenant_id = user.get("tenant_id")
    user_id = user.get("user_id")
    
    conversation_repo.delete_session(tenant_id, session_id)
    
    audit_service.log(
        tenant_id=tenant_id,
        event_type=AuditEventType.CHAT_MESSAGE,
        actor_id=user_id,
        actor_type=user.get("type", "user"),
        resource_type="session",
        resource_id=session_id,
        action="delete_session"
    )
    
    return {"message": "Session deleted", "session_id": session_id}


@router.get("/usage")
async def get_usage(
    user: Dict = Depends(get_current_user),
    billing_service=Depends(get_billing_service)
):
    """Get current usage statistics for the tenant."""
    tenant_id = user.get("tenant_id")
    
    usage = billing_service.get_tenant_usage(tenant_id)
    
    plan = billing_service.get_plan_by_id(
        billing_service.subscription_repo.get_active(tenant_id).plan_id
        if billing_service.subscription_repo.get_active(tenant_id)
        else "free"
    )
    
    requests_percent = 0
    tokens_percent = 0
    if plan and plan.monthly_requests > 0:
        requests_percent = (usage.requests_count / plan.monthly_requests) * 100
    if plan and plan.monthly_tokens > 0:
        tokens_percent = (usage.tokens_used / plan.monthly_tokens) * 100
    
    return {
        "tenant_id": tenant_id,
        "month": usage.month,
        "requests_count": usage.requests_count,
        "requests_limit": plan.monthly_requests if plan else 100,
        "requests_percent": requests_percent,
        "tokens_used": usage.tokens_used,
        "tokens_limit": plan.monthly_tokens if plan else 10000,
        "tokens_percent": tokens_percent,
        "computed_cost": usage.computed_cost
    }


@router.get("/limits")
async def get_limits(
    user: Dict = Depends(get_current_user),
    billing_service=Depends(get_billing_service)
):
    """Get plan limits for the tenant."""
    tenant_id = user.get("tenant_id")
    
    subscription = billing_service.subscription_repo.get_active(tenant_id)
    
    if subscription:
        plan = billing_service.get_plan_by_id(subscription.plan_id)
    else:
        plan = billing_service.get_plan_by_id("free")
    
    return {
        "plan_id": plan.plan_id,
        "plan_name": plan.name,
        "monthly_requests": plan.monthly_requests,
        "monthly_tokens": plan.monthly_tokens,
        "max_sessions": plan.max_sessions,
        "max_users": plan.max_users,
        "custom_branding": plan.custom_branding
    }
