"""
Processing watchdog helpers.

Celery hard time limits and worker OOM kills never run the task's except
block, so the DB can remain stuck in PROCESSING forever. The status API
uses these helpers to recover terminal failure for the mixer poll.
"""
from datetime import datetime, timedelta
from typing import Optional

# Celery worker.py sets task_time_limit=600. Allow a short grace window for
# final DB writes before treating the job as abandoned.
STALE_PROCESSING_AFTER = timedelta(seconds=720)


def is_stale_processing(
    updated_at: Optional[datetime],
    *,
    now: Optional[datetime] = None,
    limit: timedelta = STALE_PROCESSING_AFTER,
) -> bool:
    """Return True when a PROCESSING project has exceeded the worker budget."""
    if updated_at is None:
        return False
    current = now or datetime.utcnow()
    return current - updated_at > limit


STALE_PROCESSING_MESSAGE = (
    "Processamento excedeu o tempo limite ou foi interrompido. "
    "Tente novamente com um arquivo menor."
)
