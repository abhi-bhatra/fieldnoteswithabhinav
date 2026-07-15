import logging
import os

import httpx
import markdown as md

logger = logging.getLogger(__name__)

BEEHIIV_API_BASE = "https://api.beehiiv.com/v2"


def post_draft(title: str, content_markdown: str) -> str:
    api_key = os.environ["BEEHIIV_API_KEY"]
    publication_id = os.environ["BEEHIIV_PUBLICATION_ID"]

    content_html = md.markdown(content_markdown, extensions=["extra", "nl2br"])

    payload = {
        "title": title,
        "subtitle": "Azure · Kubernetes · Platform Engineering · SRE",
        "content": content_html,
        "status": "draft",
        "display_ads": False,
    }

    with httpx.Client(timeout=30) as client:
        response = client.post(
            f"{BEEHIIV_API_BASE}/publications/{publication_id}/posts",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if response.status_code not in (200, 201):
        logger.error(f"Beehiiv API error {response.status_code}: {response.text}")
        response.raise_for_status()

    draft_id = response.json()["data"]["id"]
    logger.info(f"Draft created in Beehiiv: {draft_id}")
    return draft_id
