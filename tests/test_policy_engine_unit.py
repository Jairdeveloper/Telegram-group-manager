import pytest
from app.policies.engine import PolicyEngine
from app.policies.models import Policy, PolicyRule, PolicyType, Action


def test_rate_limit_allows_within_limit():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="test_rate_limit",
        tenant_id="tenant1",
        name="rate limit",
        rules=[PolicyRule(
            policy_type=PolicyType.RATE_LIMIT,
            name="rpm",
            conditions={"requests_per_minute": 10},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    for i in range(10):
        action, _ = engine.evaluate("tenant1", {"chat_id": 123})
        assert action == Action.ALLOW
    
    action, _ = engine.evaluate("tenant1", {"chat_id": 123})
    assert action == Action.DENY


def test_rate_limit_per_chat_id():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="test_rate_limit",
        tenant_id="tenant1",
        name="rate limit",
        rules=[PolicyRule(
            policy_type=PolicyType.RATE_LIMIT,
            name="rpm",
            conditions={"requests_per_minute": 5},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    for i in range(5):
        action, _ = engine.evaluate("tenant1", {"chat_id": 123})
        assert action == Action.ALLOW
    
    action, _ = engine.evaluate("tenant1", {"chat_id": 123})
    assert action == Action.DENY
    
    action, _ = engine.evaluate("tenant1", {"chat_id": 456})
    assert action == Action.ALLOW


def test_content_filter_blocks_keyword():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="filter",
        tenant_id="tenant1",
        name="content filter",
        rules=[PolicyRule(
            policy_type=PolicyType.CONTENT_FILTER,
            name="blocked",
            conditions={"blocked_keywords": ["badword", "forbidden"]},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    action, msg = engine.evaluate("tenant1", {"message": "This contains badword"})
    assert action == Action.DENY
    
    action, _ = engine.evaluate("tenant1", {"message": "This is clean"})
    assert action == Action.ALLOW


def test_content_filter_blocks_pattern():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="filter",
        tenant_id="tenant1",
        name="content filter",
        rules=[PolicyRule(
            policy_type=PolicyType.CONTENT_FILTER,
            name="blocked_pattern",
            conditions={"blocked_patterns": [r"\d{3}-\d{2}-\d{4}"]},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    action, _ = engine.evaluate("tenant1", {"message": "My SSN is 123-45-6789"})
    assert action == Action.DENY
    
    action, _ = engine.evaluate("tenant1", {"message": "No sensitive data here"})
    assert action == Action.ALLOW


def test_quota_tracks_requests():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="quota",
        tenant_id="tenant1",
        name="monthly quota",
        rules=[PolicyRule(
            policy_type=PolicyType.QUOTA,
            name="requests",
            conditions={"monthly_requests": 5},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    for i in range(5):
        action, _ = engine.evaluate("tenant1", {})
        assert action == Action.ALLOW
    
    action, _ = engine.evaluate("tenant1", {})
    assert action == Action.DENY


def test_budget_blocks_when_exceeded():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="budget",
        tenant_id="tenant1",
        name="monthly budget",
        rules=[PolicyRule(
            policy_type=PolicyType.BUDGET,
            name="usd_limit",
            conditions={"monthly_limit_usd": 100},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    action, msg = engine.evaluate("tenant1", {"monthly_spent_usd": 50})
    assert action == Action.ALLOW
    
    action, _ = engine.evaluate("tenant1", {"monthly_spent_usd": 100})
    assert action == Action.DENY


def test_access_control_allows_chat():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="access",
        tenant_id="tenant1",
        name="chat access",
        rules=[PolicyRule(
            policy_type=PolicyType.ACCESS_CONTROL,
            name="allowed_chats",
            conditions={"allowed_chat_ids": [100, 200, 300]},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    action, _ = engine.evaluate("tenant1", {"chat_id": 100})
    assert action == Action.ALLOW
    
    action, _ = engine.evaluate("tenant1", {"chat_id": 999})
    assert action == Action.DENY


def test_access_control_blocks_chat():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="access",
        tenant_id="tenant1",
        name="chat block",
        rules=[PolicyRule(
            policy_type=PolicyType.ACCESS_CONTROL,
            name="blocked_chats",
            conditions={"blocked_chat_ids": [100, 200]},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    action, _ = engine.evaluate("tenant1", {"chat_id": 100})
    assert action == Action.DENY
    
    action, _ = engine.evaluate("tenant1", {"chat_id": 300})
    assert action == Action.ALLOW


def test_policy_priority_order():
    engine = PolicyEngine()
    
    policy1 = Policy(
        policy_id="low_priority",
        tenant_id="tenant1",
        name="low priority",
        rules=[PolicyRule(
            policy_type=PolicyType.CONTENT_FILTER,
            name="filter",
            conditions={"blocked_keywords": ["badword"]},
            action=Action.WARN,
            priority=1
        )]
    )
    
    policy2 = Policy(
        policy_id="high_priority",
        tenant_id="tenant1",
        name="high priority",
        rules=[PolicyRule(
            policy_type=PolicyType.CONTENT_FILTER,
            name="filter_strict",
            conditions={"blocked_keywords": ["hello"]},
            action=Action.DENY,
            priority=10
        )]
    )
    
    engine.register_policy(policy1)
    engine.register_policy(policy2)
    
    action, msg = engine.evaluate("tenant1", {"message": "say hello"})
    assert action == Action.DENY


def test_disabled_policy_ignored():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="disabled",
        tenant_id="tenant1",
        name="disabled policy",
        enabled=False,
        rules=[PolicyRule(
            policy_type=PolicyType.RATE_LIMIT,
            name="rate",
            conditions={"requests_per_minute": 1},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    for i in range(10):
        action, _ = engine.evaluate("tenant1", {"chat_id": 123})
        assert action == Action.ALLOW


def test_tenant_isolation():
    engine = PolicyEngine()
    policy = Policy(
        policy_id="tenant_specific",
        tenant_id="tenant1",
        name="tenant1 only",
        rules=[PolicyRule(
            policy_type=PolicyType.RATE_LIMIT,
            name="rate",
            conditions={"requests_per_minute": 2},
            action=Action.DENY,
            priority=1
        )]
    )
    engine.register_policy(policy)
    
    for i in range(2):
        action, _ = engine.evaluate("tenant1", {"chat_id": 123})
        assert action == Action.ALLOW
    
    action, _ = engine.evaluate("tenant1", {"chat_id": 123})
    assert action == Action.DENY
    
    action, _ = engine.evaluate("tenant2", {"chat_id": 123})
    assert action == Action.ALLOW


def test_no_policy_returns_allow():
    engine = PolicyEngine()
    action, msg = engine.evaluate("tenant1", {"chat_id": 123})
    assert action == Action.ALLOW
    assert msg == ""
