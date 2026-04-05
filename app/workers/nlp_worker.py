"""NLP Worker for specialized NLP processing."""

import os
import logging
import signal
import threading
import time
import psutil
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class NLPWorkerConfig:
    """Configuration for NLP Worker."""
    queue_name: str = "nlp"
    prefetch_multiplier: int = 2
    concurrency: int = 2
    max_tasks_per_child: int = 100
    task_time_limit: int = 300
    task_soft_time_limit: int = 240
    model_cache_size: int = 100
    enable_metrics: bool = True


@dataclass
class WorkerMetrics:
    """Metrics for NLP Worker."""
    tasks_processed: int = 0
    tasks_failed: int = 0
    total_processing_time: float = 0.0
    avg_processing_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_limit_mb: int = 2048
    start_time: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "tasks_processed": self.tasks_processed,
            "tasks_failed": self.tasks_failed,
            "total_processing_time": round(self.total_processing_time, 2),
            "avg_processing_time": round(self.avg_processing_time, 2),
            "cpu_usage": round(self.cpu_usage, 2),
            "memory_usage_mb": round(self.memory_usage, 2),
            "uptime_seconds": int(time.time() - self.start_time),
        }


class NLPWorker:
    """Worker for NLP processing tasks."""
    
    def __init__(self, config: Optional[NLPWorkerConfig] = None):
        self.config = config or NLPWorkerConfig()
        self.running = False
        self.model = None
        self.metrics = WorkerMetrics(memory_limit_mb=2048)
        self._shutdown_event = threading.Event()
        self._process = psutil.Process()
    
    def load_models(self) -> None:
        """Load NLP models."""
        try:
            from app.nlp.integration import get_nlp_integration
            self.model = get_nlp_integration()
            logger.info("NLP models loaded successfully", extra={
                "cache_size": self.config.model_cache_size,
            })
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}")
            raise
    
    def unload_models(self) -> None:
        """Unload NLP models and free memory."""
        if self.model:
            logger.info("Unloading NLP models...")
            self.model = None
            
            if hasattr(self._process, 'memory_info'):
                mem_info = self._process.memory_info()
                logger.info(f"Memory after cleanup: {mem_info.rss / 1024 / 1024:.2f} MB")
    
    def process_message(self, text: str) -> Dict[str, Any]:
        """Process a single message."""
        if not self.model:
            raise RuntimeError("NLP model not loaded")
        
        start_time = time.time()
        try:
            result = self.model.process_message(text)
            processing_time = time.time() - start_time
            
            self.metrics.tasks_processed += 1
            self.metrics.total_processing_time += processing_time
            self.metrics.avg_processing_time = (
                self.metrics.total_processing_time / self.metrics.tasks_processed
            )
            
            return {
                "status": "ok",
                "result": result,
                "processing_time": processing_time,
            }
        except Exception as e:
            self.metrics.tasks_failed += 1
            logger.error(f"Failed to process message: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
    
    def update_metrics(self) -> None:
        """Update worker metrics."""
        try:
            self.metrics.cpu_usage = self._process.cpu_percent(interval=0.1)
            mem_info = self._process.memory_info()
            self.metrics.memory_usage = mem_info.rss / 1024 / 1024
            
            if self.metrics.memory_usage > self.metrics.memory_limit_mb:
                logger.warning(
                    f"Memory usage {self.metrics.memory_usage:.2f} MB exceeds limit"
                )
        except Exception as e:
            logger.debug(f"Failed to update metrics: {e}")
    
    def check_health(self) -> Dict[str, Any]:
        """Check worker health status."""
        return {
            "status": "healthy" if self.running else "stopped",
            "model_loaded": self.model is not None,
            "metrics": self.metrics.to_dict(),
        }
    
    def start(self) -> None:
        """Start the NLP worker."""
        self.running = True
        self.metrics = WorkerMetrics()
        
        logger.info("Starting NLP Worker", extra={
            "queue": self.config.queue_name,
            "concurrency": self.config.concurrency,
            "prefetch": self.config.prefetch_multiplier,
        })
        
        self.load_models()
        
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
        
        logger.info("NLP Worker started successfully")
        
        while self.running and not self._shutdown_event.is_set():
            self.update_metrics()
            self._shutdown_event.wait(timeout=5)
    
    def stop(self) -> None:
        """Stop the NLP worker gracefully."""
        logger.info("NLP Worker shutting down gracefully...")
        self.running = False
        
        self.unload_models()
        
        logger.info("NLP Worker stopped", extra=self.metrics.to_dict())
    
    def _handle_shutdown(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self._shutdown_event.set()
        self.stop()


def start_nlp_worker() -> None:
    """Entry point for NLP worker."""
    config = NLPWorkerConfig(
        queue_name=os.getenv("CELERY_NLP_QUEUE", "nlp"),
        concurrency=int(os.getenv("CELERY_NLP_CONCURRENCY", "2")),
        prefetch_multiplier=int(os.getenv("CELERY_NLP_PREFETCH", "2")),
    )
    
    worker = NLPWorker(config=config)
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(process)d] %(message)s"
    )
    
    worker.start()


if __name__ == "__main__":
    start_nlp_worker()
