"""NLP metrics and monitoring for command processing."""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class IntentMetrics:
    """Metrics for a single intent."""
    intent_name: str
    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    fallback: int = 0
    avg_confidence: float = 0.0
    min_confidence: float = 1.0
    max_confidence: float = 0.0
    total_confidence: float = 0.0
    last_request_time: Optional[str] = None


@dataclass
class CommandMetrics:
    """Metrics for command processing."""
    command_name: str
    invocations: int = 0
    success_rate: float = 0.0
    avg_latency_ms: float = 0.0
    errors: int = 0


class NLPMetricsCollector:
    """Collector for NLP processing metrics."""
    
    def __init__(self):
        self._intent_metrics: Dict[str, IntentMetrics] = {}
        self._command_metrics: Dict[str, CommandMetrics] = {}
        self._request_times: Dict[str, List[float]] = defaultdict(list)
        self._start_time = datetime.now()
    
    def record_intent(self, intent: str, confidence: float, success: bool, fallback: bool = False) -> None:
        """Record an intent classification result."""
        if intent not in self._intent_metrics:
            self._intent_metrics[intent] = IntentMetrics(intent_name=intent)
        
        metrics = self._intent_metrics[intent]
        metrics.total_requests += 1
        metrics.last_request_time = datetime.now().isoformat()
        
        if success:
            metrics.successful += 1
        else:
            metrics.failed += 1
        
        if fallback:
            metrics.fallback += 1
        
        metrics.total_confidence += confidence
        metrics.avg_confidence = metrics.total_confidence / metrics.total_requests
        metrics.min_confidence = min(metrics.min_confidence, confidence)
        metrics.max_confidence = max(metrics.max_confidence, confidence)
    
    def record_command(self, command: str, latency_ms: float, success: bool) -> None:
        """Record a command execution result."""
        if command not in self._command_metrics:
            self._command_metrics[command] = CommandMetrics(command_name=command)
        
        metrics = self._command_metrics[command]
        metrics.invocations += 1
        self._request_times[command].append(latency_ms)
        
        if not success:
            metrics.errors += 1
        
        times = self._request_times[command]
        metrics.avg_latency_ms = sum(times) / len(times)
        
        if metrics.invocations > 0:
            metrics.success_rate = (metrics.invocations - metrics.errors) / metrics.invocations * 100
    
    def get_intent_summary(self) -> List[Dict]:
        """Get summary of all intent metrics."""
        return [
            {
                "intent": m.intent_name,
                "total_requests": m.total_requests,
                "successful": m.successful,
                "failed": m.failed,
                "fallback": m.fallback,
                "fallback_rate": m.fallback / m.total_requests * 100 if m.total_requests > 0 else 0,
                "avg_confidence": round(m.avg_confidence, 3),
                "min_confidence": round(m.min_confidence, 3),
                "max_confidence": round(m.max_confidence, 3),
            }
            for m in self._intent_metrics.values()
        ]
    
    def get_command_summary(self) -> List[Dict]:
        """Get summary of all command metrics."""
        return [
            {
                "command": m.command_name,
                "invocations": m.invocations,
                "success_rate": round(m.success_rate, 2),
                "avg_latency_ms": round(m.avg_latency_ms, 2),
                "errors": m.errors,
            }
            for m in self._command_metrics.values()
        ]
    
    def get_coverage_report(self) -> Dict:
        """Get coverage report."""
        total_intents = len(self._intent_metrics)
        total_requests = sum(m.total_requests for m in self._intent_metrics.values())
        
        intents_with_high_confidence = sum(
            1 for m in self._intent_metrics.values() 
            if m.avg_confidence >= 0.7 and m.total_requests > 0
        )
        
        fallback_rate = sum(m.fallback for m in self._intent_metrics.values()) / max(total_requests, 1)
        
        return {
            "total_intents_tracked": total_intents,
            "total_requests": total_requests,
            "intents_with_high_confidence": intents_with_high_confidence,
            "overall_fallback_rate": round(fallback_rate * 100, 2),
            "uptime_seconds": (datetime.now() - self._start_time).total_seconds(),
            "timestamp": datetime.now().isoformat(),
        }
    
    def get_critical_commands_alerts(self) -> List[Dict]:
        """Get alerts for critical commands with issues."""
        alerts = []
        
        critical_commands = ["welcome.toggle", "antiflood.toggle", "antispam.toggle"]
        
        for cmd in critical_commands:
            if cmd in self._command_metrics:
                metrics = self._command_metrics[cmd]
                if metrics.success_rate < 80:
                    alerts.append({
                        "command": cmd,
                        "severity": "critical",
                        "message": f"Success rate below 80%: {metrics.success_rate:.1f}%",
                        "success_rate": metrics.success_rate,
                    })
                if metrics.avg_latency_ms > 500:
                    alerts.append({
                        "command": cmd,
                        "severity": "warning",
                        "message": f"High latency: {metrics.avg_latency_ms:.1f}ms",
                        "latency_ms": metrics.avg_latency_ms,
                    })
        
        return alerts
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self._intent_metrics.clear()
        self._command_metrics.clear()
        self._request_times.clear()
        self._start_time = datetime.now()


_metrics_collector: Optional[NLPMetricsCollector] = None


def get_metrics_collector() -> NLPMetricsCollector:
    """Get or create metrics collector singleton."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = NLPMetricsCollector()
    return _metrics_collector


def track_intentClassification(intent: str, confidence: float, success: bool = True, fallback: bool = False) -> None:
    """Track an intent classification."""
    get_metrics_collector().record_intent(intent, confidence, success, fallback)


def track_command_execution(command: str, latency_ms: float, success: bool = True) -> None:
    """Track a command execution."""
    get_metrics_collector().record_command(command, latency_ms, success)
