#!/usr/bin/env python
"""Start main Celery worker."""

import sys
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    from app.celery_app import get_celery_app
    
    celery_app = get_celery_app()
    
    queues = os.getenv("CELERY_QUEUES", "default,nlp,heavy,maintenance").split(",")
    
    argv = [
        "celery",
        "-A", "app.celery_app",
        "worker",
        "-Q", ",".join(queues),
        "--loglevel", os.getenv("CELERY_LOG_LEVEL", "INFO"),
        "--concurrency", os.getenv("CELERY_CONCURRENCY", "4"),
    ]
    
    if os.getenv("CELERY_LOG_FILE"):
        argv.extend(["--logfile", os.getenv("CELERY_LOG_FILE")])
    
    print(f"Starting main worker with args: {argv}")
    celery_app.start(argv)


if __name__ == "__main__":
    main()
