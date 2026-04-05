#!/usr/bin/env python
"""Start Celery worker for NLP processing."""

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
    
    argv = [
        "celery",
        "-A", "app.celery_app",
        "worker",
        "-Q", "nlp",
        "--loglevel", os.getenv("CELERY_LOG_LEVEL", "INFO"),
        "--concurrency", os.getenv("CELERY_NLP_CONCURRENCY", "2"),
        "--prefetch-multiplier", "2",
        "-O", "fair",
    ]
    
    if os.getenv("CELERY_LOG_FORMAT"):
        argv.extend(["--logfile", os.getenv("CELERY_LOG_FILE", "-")])
    
    print(f"Starting NLP worker with args: {argv}")
    celery_app.start(argv)


if __name__ == "__main__":
    main()
