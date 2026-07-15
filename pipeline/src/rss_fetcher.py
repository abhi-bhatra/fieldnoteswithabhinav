import calendar
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import feedparser

logger = logging.getLogger(__name__)

FEEDS = [
    ("Azure Updates",        "https://azure.microsoft.com/en-us/updates/feed/"),
    ("Azure Blog",           "https://azure.microsoft.com/en-us/blog/feed/"),
    ("Kubernetes Blog",      "https://kubernetes.io/feed.xml"),
    ("The New Stack",        "https://thenewstack.io/feed/"),
    ("HN: K8s/DevOps/Azure", "https://hnrss.org/newest?q=kubernetes+OR+devops+OR+azure&points=50"),
    ("r/kubernetes",         "https://www.reddit.com/r/kubernetes/.rss"),
    ("r/devops",             "https://www.reddit.com/r/devops/.rss"),
    ("r/azure",              "https://www.reddit.com/r/AZURE/.rss"),
]

ARTICLES_PER_FEED = 10


@dataclass
class Article:
    title: str
    url: str
    summary: str
    source: str
    published: datetime


def fetch_articles(lookback_days: int = 7) -> list[Article]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    articles: list[Article] = []

    for source_name, url in FEEDS:
        try:
            feed = feedparser.parse(url)
            count = 0
            for entry in feed.entries:
                if count >= ARTICLES_PER_FEED:
                    break
                published = _parse_date(entry)
                if published and published < cutoff:
                    continue
                articles.append(Article(
                    title=entry.get("title", "").strip(),
                    url=entry.get("link", ""),
                    summary=_clean_summary(entry.get("summary", "")),
                    source=source_name,
                    published=published or datetime.now(timezone.utc),
                ))
                count += 1
            logger.info(f"Fetched {count} articles from {source_name}")
        except Exception as e:
            logger.warning(f"Failed to fetch {source_name}: {e}")

    articles.sort(key=lambda a: a.published, reverse=True)
    return articles


def _parse_date(entry) -> datetime | None:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime.fromtimestamp(
            calendar.timegm(entry.published_parsed), tz=timezone.utc
        )
    return None


def _clean_summary(raw: str) -> str:
    import re
    text = re.sub(r"<[^>]+>", "", raw)  # strip HTML tags
    text = " ".join(text.split())        # collapse whitespace
    return text[:600]
