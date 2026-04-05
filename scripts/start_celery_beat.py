#!/usr/bin/env python
"""Start Celery beat scheduler."""

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
        "beat",
        "--loglevel", os.getenv("CELERY_BEAT_LOG_LEVEL", "INFO"),
        "--scheduler", os.getenv("CELERY_BEAT_SCHEDULER", "celery.schedulers:DatabaseScheduler"),
    ]
    
    if os.getenv("CELERY_BEAT_LOG_FILE"):
        argv.extend(["--logfile", os.getenv("CELERY_BEAT_LOG_FILE")])
    
    print(f"Starting Celery beat with args: {argv}")
    celery_app.start(argv)


if __name__ == "__main__":
    main()
