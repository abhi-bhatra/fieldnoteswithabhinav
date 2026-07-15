import calendar
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import httpx

logger = logging.getLogger(__name__)

SEEN_URLS_FILE = Path(__file__).parent.parent / "state" / "seen_urls.txt"
SEEN_URLS_MAX  = 500  # cap to avoid unbounded growth


def _load_seen_urls() -> set[str]:
    if SEEN_URLS_FILE.exists():
        return set(SEEN_URLS_FILE.read_text().splitlines())
    return set()


def _save_seen_urls(seen: set[str]) -> None:
    urls = list(seen)[-SEEN_URLS_MAX:]  # keep only latest N
    SEEN_URLS_FILE.write_text("\n".join(urls))


# ---------------------------------------------------------------------------
# Feed list — (source_name, url, requires_custom_headers)
# ---------------------------------------------------------------------------
FEEDS = [
    # Azure
    ("Azure Updates",     "https://azure.microsoft.com/en-us/updates/feed/",           False),
    ("Azure Blog",        "https://azure.microsoft.com/en-us/blog/feed/",               False),

    # Kubernetes
    ("Kubernetes Blog",   "https://kubernetes.io/feed.xml",                             False),
    ("CNCF Blog",         "https://www.cncf.io/feed/",                                  False),

    # DevOps & Platform Engineering
    ("The New Stack",     "https://thenewstack.io/feed/",                               False),
    ("DevOps Weekly",     "https://www.devopsweeklyarchive.com/feed/",                  False),
    ("InfoQ DevOps",      "https://www.infoq.com/devops/rss/",                          False),

    # Hacker News — lowered threshold to 25 points for more results
    ("Hacker News",       "https://hnrss.org/newest?q=kubernetes+OR+devops+OR+azure+OR+platform+engineering&points=25", False),

    # Reddit — requires browser-like user-agent
    ("r/kubernetes",      "https://www.reddit.com/r/kubernetes/.rss",                   True),
    ("r/devops",          "https://www.reddit.com/r/devops/.rss",                       True),
    ("r/azure",           "https://www.reddit.com/r/AZURE/.rss",                        True),
    ("r/sre",             "https://www.reddit.com/r/sre/.rss",                          True),
    ("r/platformeng",     "https://www.reddit.com/r/platformengineering/.rss",          True),
]

ARTICLES_PER_FEED = 10

REDDIT_HEADERS = {
    "User-Agent": "fieldnoteswithabhinav/1.0 (newsletter bot; +https://github.com/abhi-bhatra/fieldnoteswithabhinav)"
}


@dataclass
class Article:
    title: str
    url: str
    summary: str
    source: str
    published: datetime


def fetch_articles(lookback_days: int = 3) -> list[Article]:
    cutoff   = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    seen     = _load_seen_urls()
    articles: list[Article] = []
    new_urls: set[str] = set()

    for source_name, url, needs_headers in FEEDS:
        try:
            if needs_headers:
                feed = _fetch_with_headers(url, REDDIT_HEADERS)
            else:
                feed = feedparser.parse(url)

            count = 0
            for entry in feed.entries:
                if count >= ARTICLES_PER_FEED:
                    break
                article_url = entry.get("link", "")
                if article_url in seen:
                    continue  # already used in a previous issue
                published = _parse_date(entry)
                if published and published < cutoff:
                    continue
                articles.append(Article(
                    title=entry.get("title", "").strip(),
                    url=article_url,
                    summary=_clean_summary(entry.get("summary", "")),
                    source=source_name,
                    published=published or datetime.now(timezone.utc),
                ))
                new_urls.add(article_url)
                count += 1

            logger.info(f"Fetched {count} new articles from {source_name}")
        except Exception as e:
            logger.warning(f"Failed to fetch {source_name}: {e}")

    # persist seen URLs so next run skips these
    _save_seen_urls(seen | new_urls)

    articles.sort(key=lambda a: a.published, reverse=True)
    return articles


def _fetch_with_headers(url: str, headers: dict) -> feedparser.FeedParserDict:
    response = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
    response.raise_for_status()
    return feedparser.parse(response.content)


def _parse_date(entry) -> datetime | None:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime.fromtimestamp(
            calendar.timegm(entry.published_parsed), tz=timezone.utc
        )
    return None


def _clean_summary(raw: str) -> str:
    import re
    text = re.sub(r"<[^>]+>", "", raw)
    text = " ".join(text.split())
    return text[:600]
