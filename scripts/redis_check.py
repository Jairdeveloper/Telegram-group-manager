#!/usr/bin/env python3
"""Script to validate Redis connectivity and configuration."""

import sys
import os
import time
import logging
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.redis import RedisConnectionManager, get_redis_manager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_connection(manager: RedisConnectionManager) -> bool:
    """Test basic Redis connection."""
    logger.info("Testing Redis connection...")
    try:
        conn = manager.get_connection()
        result = conn.ping()
        logger.info(f"Ping result: {result}")
        return result
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


def test_operations(manager: RedisConnectionManager) -> bool:
    """Test Redis basic operations."""
    logger.info("Testing Redis operations...")
    try:
        conn = manager.get_connection()
        
        test_key = "robot:health_check:test"
        test_value = f"test_value_{int(time.time())}"
        
        conn.set(test_key, test_value, ex=10)
        retrieved = conn.get(test_key)
        
        if retrieved != test_value:
            logger.error(f"Value mismatch: set {test_value}, got {retrieved}")
            return False
        
        conn.delete(test_key)
        logger.info("Operations test passed")
        
        return True
    except Exception as e:
        logger.error(f"Operations test failed: {e}")
        return False


def test_connection_pool(manager: RedisConnectionManager) -> bool:
    """Test connection pool functionality."""
    logger.info("Testing connection pool...")
    try:
        manager.initialize_pool()
        
        connections = []
        for i in range(5):
            conn = manager.get_connection()
            conn.ping()
            connections.append(conn)
        
        logger.info(f"Successfully created {len(connections)} connections from pool")
        
        return True
    except Exception as e:
        logger.error(f"Connection pool test failed: {e}")
        return False


def test_pipeline(manager: RedisConnectionManager) -> bool:
    """Test Redis pipeline."""
    logger.info("Testing Redis pipeline...")
    try:
        conn = manager.get_connection()
        
        test_keys = [f"robot:health_check:pipe:{i}" for i in range(5)]
        
        pipe = conn.pipeline()
        for key in test_keys:
            pipe.set(key, f"value_{key}", ex=10)
        pipe.execute()
        
        pipe = conn.pipeline()
        for key in test_keys:
            pipe.get(key)
        results = pipe.execute()
        
        for key in test_keys:
            conn.delete(key)
        
        logger.info("Pipeline test passed")
        return True
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        return False


def check_redis_server() -> bool:
    """Check if Redis server is running."""
    logger.info("Checking Redis server availability...")
    
    try:
        import redis
        r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), 
                        port=int(os.getenv("REDIS_PORT", "6379")))
        r.ping()
        logger.info("Redis server is running")
        return True
    except Exception as e:
        logger.error(f"Redis server not available: {e}")
        
        logger.info("""
To start Redis server:
  - Ubuntu/Debian: sudo apt-get install redis-server && sudo systemctl start redis
  - macOS: brew services start redis
  - Docker: docker run -d -p 6379:6379 --name redis redis:latest
  - Or use: redis-server --daemonize yes
        """)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate Redis connectivity")
    parser.add_argument("--skip-server-check", action="store_true",
                        help="Skip Redis server availability check")
    args = parser.parse_args()

    if not args.skip_server_check:
        if not check_redis_server():
            sys.exit(1)

    logger.info("=" * 50)
    logger.info("Starting Redis validation tests")
    logger.info("=" * 50)

    manager = get_redis_manager()
    
    tests = [
        ("Connection", test_connection),
        ("Operations", test_operations),
        ("Connection Pool", test_connection_pool),
        ("Pipeline", test_pipeline),
    ]
    
    results = {}
    for name, test_func in tests:
        logger.info(f"\n--- Running: {name} ---")
        results[name] = test_func(manager)
    
    logger.info("\n" + "=" * 50)
    logger.info("Results Summary")
    logger.info("=" * 50)
    
    all_passed = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        logger.info(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    health = manager.health_check()
    logger.info(f"\nHealth Check: {health}")
    
    stats = manager.get_stats()
    logger.info(f"\nRedis Stats:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value}")
    
    if all_passed:
        logger.info("\n✓ All tests passed!")
        sys.exit(0)
    else:
        logger.error("\n✗ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
