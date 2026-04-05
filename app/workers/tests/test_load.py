"""Load tests for NLP Worker."""

import time
import logging
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any
import threading
import statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoadTestResult:
    """Results from load testing."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.errors: int = 0
        self.successful: int = 0
        self.start_time: float = 0
        self.end_time: float = 0
    
    def add_result(self, success: bool, response_time: float) -> None:
        """Add a test result."""
        if success:
            self.successful += 1
            self.response_times.append(response_time)
        else:
            self.errors += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics."""
        if not self.response_times:
            return {
                "total_requests": self.successful + self.errors,
                "successful": self.successful,
                "errors": self.errors,
                "error_rate": 1.0,
            }
        
        return {
            "total_requests": self.successful + self.errors,
            "successful": self.successful,
            "errors": self.errors,
            "error_rate": self.errors / (self.successful + self.errors),
            "avg_response_time": statistics.mean(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "median_response_time": statistics.median(self.response_times),
            "p95_response_time": sorted(self.response_times)[int(len(self.response_times) * 0.95)] if len(self.response_times) > 20 else max(self.response_times),
            "throughput": self.successful / (self.end_time - self.start_time) if self.end_time > self.start_time else 0,
            "total_duration": self.end_time - self.start_time,
        }


def mock_nlp_integration():
    """Create mock NLP integration."""
    mock = MagicMock()
    mock.process_message.return_value = MagicMock(
        intent="test",
        action_result={"action": "test", "confidence": 0.95}
    )
    return mock


def run_concurrent_load_test(
    num_threads: int = 10,
    requests_per_thread: int = 100,
    delay_between_requests: float = 0.01,
) -> LoadTestResult:
    """Run concurrent load test on NLP worker."""
    result = LoadTestResult()
    result.start_time = time.time()
    
    def worker_thread():
        """Worker thread function."""
        with patch("app.workers.nlp_worker.get_nlp_integration") as mock_get:
            mock_get.return_value = mock_nlp_integration()
            
            from app.workers.nlp_worker import NLPWorker
            
            worker = NLPWorker()
            worker.load_models()
            
            for i in range(requests_per_thread):
                start = time.time()
                try:
                    worker.process_message(f"Test message {i}")
                    response_time = time.time() - start
                    result.add_result(True, response_time)
                except Exception as e:
                    result.add_result(False, 0)
                    logger.error(f"Error: {e}")
                
                time.sleep(delay_between_requests)
            
            worker.unload_models()
    
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker_thread)
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    result.end_time = time.time()
    return result


def run_sequential_load_test(
    num_requests: int = 1000,
    delay_between_requests: float = 0.001,
) -> LoadTestResult:
    """Run sequential load test on NLP worker."""
    result = LoadTestResult()
    result.start_time = time.time()
    
    with patch("app.workers.nlp_worker.get_nlp_integration") as mock_get:
        mock_get.return_value = mock_nlp_integration()
        
        from app.workers.nlp_worker import NLPWorker
        
        worker = NLPWorker()
        worker.load_models()
        
        for i in range(num_requests):
            start = time.time()
            try:
                worker.process_message(f"Test message {i}")
                response_time = time.time() - start
                result.add_result(True, response_time)
            except Exception as e:
                result.add_result(False, 0)
                logger.error(f"Error: {e}")
            
            time.sleep(delay_between_requests)
        
        worker.unload_models()
    
    result.end_time = time.time()
    return result


def run_memory_stress_test(duration_seconds: int = 30) -> Dict[str, Any]:
    """Run memory stress test."""
    import psutil
    
    result = {
        "initial_memory_mb": 0,
        "peak_memory_mb": 0,
        "final_memory_mb": 0,
        "samples": [],
    }
    
    process = psutil.Process()
    result["initial_memory_mb"] = process.memory_info().rss / 1024 / 1024
    
    with patch("app.workers.nlp_worker.get_nlp_integration") as mock_get:
        mock_get.return_value = mock_nlp_integration()
        
        from app.workers.nlp_worker import NLPWorker
        
        worker = NLPWorker()
        worker.load_models()
        
        start = time.time()
        iteration = 0
        
        while time.time() - start < duration_seconds:
            worker.process_message(f"Stress test message {iteration}")
            iteration += 1
            
            mem = process.memory_info().rss / 1024 / 1024
            result["peak_memory_mb"] = max(result["peak_memory_mb"], mem)
            result["samples"].append(mem)
            
            time.sleep(0.01)
        
        worker.unload_models()
    
    result["final_memory_mb"] = process.memory_info().rss / 1024 / 1024
    result["iterations"] = iteration
    result["duration_seconds"] = duration_seconds
    
    return result


def run_all_load_tests() -> Dict[str, Any]:
    """Run all load tests."""
    logger.info("Running load tests...")
    
    results = {}
    
    logger.info("Running concurrent load test (10 threads, 100 requests each)...")
    results["concurrent"] = run_concurrent_load_test(
        num_threads=10,
        requests_per_thread=100,
    ).get_stats()
    
    logger.info("Running sequential load test (1000 requests)...")
    results["sequential"] = run_sequential_load_test(
        num_requests=1000,
    ).get_stats()
    
    logger.info("Running memory stress test (30 seconds)...")
    results["memory_stress"] = run_memory_stress_test(duration_seconds=30)
    
    return results


if __name__ == "__main__":
    import json
    
    results = run_all_load_tests()
    print("\n=== Load Test Results ===\n")
    print(json.dumps(results, indent=2))
