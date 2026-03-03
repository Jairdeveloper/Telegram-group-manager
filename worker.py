"""Entrypoint for RQ worker (Docker / k8s)."""
from redis import Redis
from rq import Worker, Queue

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
