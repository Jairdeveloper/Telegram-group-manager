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
QUEUE_NAMES = WORKER_SETTINGS.queue_names
REDIS_URL = WORKER_SETTINGS.redis_url
REDIS_CONN = Redis.from_url(REDIS_URL)


def main():
    """Entry point para CLI."""
    import logging
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting RQ worker for queues: {QUEUE_NAMES}")
    
    queues = [Queue(name, connection=REDIS_CONN) for name in QUEUE_NAMES]
    worker = Worker(queues, connection=REDIS_CONN)
    worker.work()


if __name__ == "__main__":
    main()
