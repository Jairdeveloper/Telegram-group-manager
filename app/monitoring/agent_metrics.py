from __future__ import annotations

from typing import Optional

try:
    from prometheus_client import Counter, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


class MockMetric:
    def labels(self, **kwargs):
        return self

    def inc(self, *args, **kwargs):
        pass

    def observe(self, *args, **kwargs):
        pass


def _get_metric(real_metric, mock_metric):
    if PROMETHEUS_AVAILABLE:
        return real_metric
    return mock_metric


AGENT_THOUGHTS = _get_metric(
    Counter("agent_thoughts_total", "Total agent thoughts", ["source"]),
    MockMetric(),
)

AGENT_ACTIONS = _get_metric(
    Counter("agent_actions_total", "Total agent actions", ["action"]),
    MockMetric(),
)

RAG_RETRIEVAL_LATENCY = _get_metric(
    Histogram("rag_retrieval_latency_seconds", "RAG retrieval latency", ["tenant_id"]),
    MockMetric(),
)

TOOL_EXECUTION_DURATION = _get_metric(
    Histogram("tool_execution_duration_seconds", "Tool execution duration", ["tool"]),
    MockMetric(),
)

LLM_TOKENS_USED = _get_metric(
    Counter("llm_tokens_used_total", "Estimated LLM tokens used", ["provider", "model", "source"]),
    MockMetric(),
)


def estimate_tokens(text: Optional[str]) -> int:
    if not text:
        return 0
    # Rough heuristic: 1 token ~= 4 chars
    return max(1, len(text) // 4)


def record_llm_usage(provider: str, model: str, prompt: str, response: str, source: str) -> None:
    tokens = estimate_tokens(prompt) + estimate_tokens(response)
    if tokens <= 0:
        return
    LLM_TOKENS_USED.labels(provider=provider, model=model, source=source).inc(tokens)


def record_tool_execution(tool: str, duration_seconds: float) -> None:
    TOOL_EXECUTION_DURATION.labels(tool=tool).observe(duration_seconds)


def record_rag_latency(tenant_id: str, duration_seconds: float) -> None:
    RAG_RETRIEVAL_LATENCY.labels(tenant_id=tenant_id).observe(duration_seconds)


def record_agent_thought(source: str) -> None:
    AGENT_THOUGHTS.labels(source=source).inc()


def record_agent_action(action: str) -> None:
    AGENT_ACTIONS.labels(action=action).inc()
