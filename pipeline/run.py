import logging
import os
import sys

from src.ai_processor import generate_newsletter
from src.banner_generator import generate_banner
from src.distribution_pack import generate_distribution_pack
from src.draft_writer import save_draft
from src.rss_fetcher import fetch_articles
from src.state_manager import get_and_increment_issue_number

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

BEEHIIV_BASE = "https://fieldnoteswithabhinav.beehiiv.com/p/field-notes-weekly"


def main() -> None:
    articles = fetch_articles(lookback_days=7)
    logger.info(f"Fetched {len(articles)} articles")

    if not articles:
        logger.warning("No articles found this week — skipping")
        sys.exit(0)

    issue_number = get_and_increment_issue_number()
    result = generate_newsletter(articles, issue_number)

    beehiiv_url = f"{BEEHIIV_BASE}-{issue_number}"

    draft_path = save_draft(result["title"], result["content_markdown"])
    banner_path = generate_banner(result["title"], result["content_markdown"], issue_number)
    dist_path = generate_distribution_pack(result["content_markdown"], issue_number, beehiiv_url)

    logger.info(f"Done. Issue #{issue_number}")
    logger.info(f"  Draft:      {draft_path}")
    logger.info(f"  Banner:     {banner_path}")
    logger.info(f"  Distribute: {dist_path}")


if __name__ == "__main__":
    main()
