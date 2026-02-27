"""Entrypoint for RQ worker (Docker / k8s)."""
import os
from redis import Redis
from rq import Worker, Queue

listen = ["telegram_tasks"]
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
conn = Redis.from_url(redis_url)

if __name__ == "__main__":
    # Create Queue objects bound to the Redis connection and start the worker
    queues = [Queue(name, connection=conn) for name in listen]
    worker = Worker(queues, connection=conn)
    worker.work()
