import logging
import sys

from src.ai_processor import generate_newsletter
from src.beehiiv_client import post_draft
from src.rss_fetcher import fetch_articles
from src.state_manager import get_and_increment_issue_number

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    articles = fetch_articles(lookback_days=7)
    logger.info(f"Fetched {len(articles)} articles")

    if not articles:
        logger.warning("No articles found this week — skipping")
        sys.exit(0)

    issue_number = get_and_increment_issue_number()
    result = generate_newsletter(articles, issue_number)
    draft_id = post_draft(result["title"], result["content_markdown"])

    logger.info(f"Done. Issue #{issue_number} posted as Beehiiv draft {draft_id}")


if __name__ == "__main__":
    main()
