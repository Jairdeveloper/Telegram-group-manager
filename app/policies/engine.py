from typing import Optional, List, Dict, Any, Tuple
from app.policies.models import Policy, PolicyRule, Action, PolicyType
from datetime import datetime, timedelta
import threading


class PolicyEngine:
    def __init__(self):
        self._policies: Dict[str, Policy] = {}
        self._rate_limit_store: Dict[str, List[datetime]] = {}
        self._quota_store: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def register_policy(self, policy: Policy) -> None:
        with self._lock:
            self._policies[policy.policy_id] = policy

    def unregister_policy(self, policy_id: str) -> None:
        with self._lock:
            self._policies.pop(policy_id, None)

    def get_policy(self, policy_id: str) -> Optional[Policy]:
        return self._policies.get(policy_id)

    def list_policies(self, tenant_id: Optional[str] = None) -> List[Policy]:
        policies = list(self._policies.values())
        if tenant_id:
            policies = [p for p in policies if p.tenant_id == tenant_id]
        return policies

    def evaluate(self, tenant_id: str, context: Dict[str, Any]) -> Tuple[Action, str]:
        policies = [p for p in self._policies.values() 
                   if p.tenant_id == tenant_id and p.enabled]
        
        if not policies:
            return Action.ALLOW, ""
        
        policies.sort(key=lambda p: max((r.priority for r in p.rules), default=0), reverse=True)
        
        for policy in policies:
            for rule in policy.rules:
                if self._evaluate_rule(rule, context):
                    return rule.action, rule.message or f"Policy {rule.name} triggered"
        
        return Action.ALLOW, ""

    def _evaluate_rule(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        if rule.policy_type == PolicyType.RATE_LIMIT:
            return self._check_rate_limit(rule, context)
        elif rule.policy_type == PolicyType.QUOTA:
            return self._check_quota(rule, context)
        elif rule.policy_type == PolicyType.CONTENT_FILTER:
            return self._check_content_filter(rule, context)
        elif rule.policy_type == PolicyType.BUDGET:
            return self._check_budget(rule, context)
        elif rule.policy_type == PolicyType.ACCESS_CONTROL:
            return self._check_access_control(rule, context)
        return False

    def _check_rate_limit(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        policy_id = rule.conditions.get("_policy_id", "default")
        key = f"{policy_id}:{context.get('chat_id', 'default')}"
        now = datetime.utcnow()
        
        with self._lock:
            if key not in self._rate_limit_store:
                self._rate_limit_store[key] = []
            
            self._rate_limit_store[key] = [
                ts for ts in self._rate_limit_store[key]
                if now - ts < timedelta(minutes=1)
            ]
            
            limit = rule.conditions.get("requests_per_minute", 60)
            if len(self._rate_limit_store[key]) >= limit:
                return True
            
            self._rate_limit_store[key].append(now)
            return False

    def _check_quota(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        policy_id = rule.conditions.get("_policy_id", "default")
        key = f"{policy_id}:{context.get('tenant_id')}"
        month = datetime.utcnow().strftime("%Y-%m")
        
        with self._lock:
            if key not in self._quota_store:
                self._quota_store[key] = {"month": month, "requests": 0, "tokens": 0}
            
            quota = self._quota_store[key]
            if quota["month"] != month:
                quota["month"] = month
                quota["requests"] = 0
                quota["tokens"] = 0
            
            limit = rule.conditions.get("monthly_requests", 10000)
            if quota["requests"] >= limit:
                return True
            
            quota["requests"] += 1
            
            tokens = context.get("tokens", 0)
            if tokens > 0:
                quota["tokens"] += tokens
                token_limit = rule.conditions.get("monthly_tokens", 1000000)
                if quota["tokens"] >= token_limit:
                    return True
            
            return False

    def _check_content_filter(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        message = context.get("message", "").lower()
        blocked = rule.conditions.get("blocked_keywords", [])
        
        for keyword in blocked:
            if keyword.lower() in message:
                return True
        
        blocked_patterns = rule.conditions.get("blocked_patterns", [])
        import re
        for pattern in blocked_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True
        
        max_length = rule.conditions.get("max_message_length", 4000)
        if len(message) > max_length:
            return True
        
        return False

    def _check_budget(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        spent = context.get("monthly_spent_usd", 0)
        limit = rule.conditions.get("monthly_limit_usd", 100)
        
        if spent >= limit:
            return True
        
        warning_threshold = rule.conditions.get("warning_threshold", 0.8)
        if spent >= limit * warning_threshold:
            return False
        
        return False

    def _check_access_control(self, rule: PolicyRule, context: Dict[str, Any]) -> bool:
        chat_id = context.get("chat_id")
        user_id = context.get("user_id")
        tool_name = context.get("tool_name")
        
        allowed_chats = rule.conditions.get("allowed_chat_ids")
        if allowed_chats and chat_id not in allowed_chats:
            return True
        
        blocked_chats = rule.conditions.get("blocked_chat_ids")
        if blocked_chats and chat_id in blocked_chats:
            return True
        
        blocked_tools = rule.conditions.get("blocked_tools", [])
        if blocked_tools and tool_name in blocked_tools:
            return True
        
        allowed_tools = rule.conditions.get("allowed_tools", [])
        if allowed_tools and tool_name not in allowed_tools:
            return True
        
        return False

    def get_rate_limit_stats(self, policy_id: str, chat_id: str) -> Dict[str, Any]:
        key = f"{policy_id}:{chat_id}"
        now = datetime.utcnow()
        
        with self._lock:
            if key not in self._rate_limit_store:
                return {"remaining": 60, "reset_in_seconds": 60}
            
            recent = [ts for ts in self._rate_limit_store[key] 
                     if now - ts < timedelta(minutes=1)]
            
            return {
                "used": len(recent),
                "remaining": max(0, 60 - len(recent)),
                "reset_in_seconds": 60
            }

    def get_quota_stats(self, policy_id: str, tenant_id: str) -> Dict[str, Any]:
        key = f"{policy_id}:{tenant_id}"
        month = datetime.utcnow().strftime("%Y-%m")
        
        with self._lock:
            if key not in self._quota_store:
                return {"requests": 0, "tokens": 0, "limit": 10000}
            
            quota = self._quota_store[key]
            if quota["month"] != month:
                return {"requests": 0, "tokens": 0, "limit": 10000}
            
            return {
                "requests": quota["requests"],
                "tokens": quota["tokens"],
                "requests_limit": 10000,
                "tokens_limit": 1000000
            }

    def reset_rate_limit(self, policy_id: str, chat_id: str) -> None:
        key = f"{policy_id}:{chat_id}"
        with self._lock:
            self._rate_limit_store.pop(key, None)

    def reset_quota(self, policy_id: str, tenant_id: str) -> None:
        key = f"{policy_id}:{tenant_id}"
        with self._lock:
            self._quota_store.pop(key, None)
