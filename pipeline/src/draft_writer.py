import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

DRAFTS_DIR = Path(__file__).parent.parent.parent / "drafts"


def save_draft(title: str, content_markdown: str) -> Path:
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = DRAFTS_DIR / f"{date_str}.md"

    body = f"# {title}\n\n_{date_str}_\n\n---\n\n{content_markdown}\n"
    filename.write_text(body, encoding="utf-8")

    logger.info(f"Draft saved: {filename}")
    return filename
