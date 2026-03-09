import pytest
from app.ops.chat_integration import (
    ChatService,
    ChatContext,
    ChatResponse,
    handle_chat_message,
    get_default_chat_service,
)
from app.policies.models import Policy, PolicyRule, PolicyType, Action
from app.tools.builtins import register_builtin_tools


def test_chat_service_blocks_sensitive_input():
    service = ChatService()
    context = ChatContext(chat_id=123, tenant_id="default")
    
    response = service.handle_message("My SSN is 123-45-6789", context)
    
    assert response.blocked is True
    assert "blocked" in response.response.lower()


def test_chat_service_blocks_rate_limit():
    service = ChatService()
    
    policy = Policy(
        policy_id="rate_limit",
        tenant_id="default",
        name="rate limit",
        rules=[PolicyRule(
            policy_type=PolicyType.RATE_LIMIT,
            name="rpm",
            conditions={"requests_per_minute": 2},
            action=Action.DENY,
            priority=10
        )]
    )
    service.register_policy(policy)
    
    context = ChatContext(chat_id=123, tenant_id="default")
    
    response1 = service.handle_message("hello", context)
    assert response1.success is True
    
    response2 = service.handle_message("hello again", context)
    assert response2.success is True
    
    response3 = service.handle_message("hello third time", context)
    assert response3.blocked is True


def test_chat_service_executes_tools():
    service = ChatService()
    register_builtin_tools(service.tool_registry)
    
    context = ChatContext(chat_id=123, tenant_id="default")
    
    response = service.handle_message("calculate 5 + 3", context)
    
    assert response.success is True
    assert len(response.tools_executed) > 0


def test_chat_service_plan_creation():
    service = ChatService()
    register_builtin_tools(service.tool_registry)
    
    context = ChatContext(chat_id=123, tenant_id="default")
    
    response = service.handle_message("search for python", context)
    
    assert response.plan_id is not None


def test_chat_service_get_policy_stats():
    service = ChatService()
    
    policy = Policy(
        policy_id="test_policy",
        tenant_id="tenant1",
        name="Test Policy",
        rules=[PolicyRule(
            policy_type=PolicyType.RATE_LIMIT,
            name="rate",
            conditions={"requests_per_minute": 60},
            action=Action.ALLOW,
            priority=1
        )]
    )
    service.register_policy(policy)
    
    stats = service.get_policy_stats("tenant1")
    
    assert stats["policies_count"] == 1
    assert stats["policies"][0]["name"] == "Test Policy"


def test_handle_chat_message_function():
    response = handle_chat_message(123, "hello")
    
    assert "success" in response
    assert "response" in response


def test_chat_context_creation():
    context = ChatContext(chat_id=123, tenant_id="tenant1", user_id="user1")
    
    assert context.chat_id == 123
    assert context.tenant_id == "tenant1"
    assert context.user_id == "user1"


def test_chat_service_blocks_content_filter():
    service = ChatService()
    
    policy = Policy(
        policy_id="content_filter",
        tenant_id="default",
        name="content filter",
        rules=[PolicyRule(
            policy_type=PolicyType.CONTENT_FILTER,
            name="bad_words",
            conditions={"blocked_keywords": ["badword"]},
            action=Action.DENY,
            priority=10
        )]
    )
    service.register_policy(policy)
    
    context = ChatContext(chat_id=123, tenant_id="default")
    
    response = service.handle_message("This contains badword", context)
    
    assert response.blocked is True


def test_chat_service_allows_clean_message():
    service = ChatService()
    register_builtin_tools(service.tool_registry)
    
    context = ChatContext(chat_id=123, tenant_id="default")
    
    response = service.handle_message("Hello, how are you?", context)
    
    assert response.success is True


def test_default_chat_service_singleton():
    service1 = get_default_chat_service()
    service2 = get_default_chat_service()
    
    assert service1 is service2


def test_chat_response_dataclass():
    response = ChatResponse(
        success=True,
        response="Test response",
        plan_id="plan_123",
        tools_executed=["calculator", "search"],
    )
    
    assert response.success is True
    assert response.response == "Test response"
    assert response.plan_id == "plan_123"
    assert "calculator" in response.tools_executed


def test_chat_service_multiple_tenants():
    service = ChatService()
    
    policy1 = Policy(
        policy_id="tenant1_policy",
        tenant_id="tenant1",
        name="Tenant 1 Policy",
        rules=[PolicyRule(
            policy_type=PolicyType.RATE_LIMIT,
            name="rate",
            conditions={"requests_per_minute": 1},
            action=Action.DENY,
            priority=10
        )]
    )
    service.register_policy(policy1)
    
    context1 = ChatContext(chat_id=123, tenant_id="tenant1")
    context2 = ChatContext(chat_id=123, tenant_id="tenant2")
    
    response1 = service.handle_message("hello", context1)
    assert response1.success is True
    
    response2 = service.handle_message("hello", context1)
    assert response2.blocked is True
    
    response3 = service.handle_message("hello", context2)
    assert response3.success is True
