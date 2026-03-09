from dataclasses import dataclass
from typing import Optional, List


@dataclass
class RateLimitConfig:
    requests_per_minute: int
    requests_per_hour: int
    burst_limit: Optional[int] = None


@dataclass
class QuotaConfig:
    monthly_requests: int
    monthly_tokens: int


@dataclass
class BudgetConfig:
    monthly_limit_usd: float
    warning_threshold: float = 0.8


@dataclass
class ContentFilterConfig:
    blocked_keywords: List[str]
    blocked_patterns: List[str]
    max_message_length: int = 4000
    allow_urls: bool = True


@dataclass
class AccessControlConfig:
    allowed_chat_ids: Optional[List[int]] = None
    blocked_chat_ids: Optional[List[int]] = None
    require_approval: bool = False
