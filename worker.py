"""Entrypoint for RQ worker (Docker / k8s)."""
import sys

from redis import Redis
try:
    from rq import Worker, Queue
except Exception as exc:
    print(f"Failed to import RQ worker runtime: {exc}")
    print("Install compatible dependencies and run worker in a supported runtime (recommended: Docker/Linux).")
    sys.exit(1)

from app.config.settings import load_worker_settings

WORKER_SETTINGS = load_worker_settings()
listen = WORKER_SETTINGS.queue_names
redis_url = WORKER_SETTINGS.redis_url
conn = Redis.from_url(redis_url)

if __name__ == "__main__":
    # Create Queue objects bound to the Redis connection and start the worker
    queues = [Queue(name, connection=conn) for name in listen]
    worker = Worker(queues, connection=conn)
    worker.work()
