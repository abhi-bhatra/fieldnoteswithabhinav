"""
Tracks newsletter issue number in a file committed to the repo.
GitHub Actions reads it, increments it, and commits it back after each run.
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

STATE_FILE = Path(__file__).parent.parent / "state" / "issue_number.txt"


def get_and_increment_issue_number() -> int:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    current = 0
    if STATE_FILE.exists():
        current = int(STATE_FILE.read_text().strip())

    next_issue = current + 1
    STATE_FILE.write_text(str(next_issue))

    logger.info(f"Issue number: {next_issue}")
    return next_issue
