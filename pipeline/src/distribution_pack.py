"""
Generates a ready-to-copy distribution pack for each platform.
One additional OpenAI call per issue — runs after newsletter generation.
"""
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from openai import AzureOpenAI

logger = logging.getLogger(__name__)

DRAFTS_DIR = Path(__file__).parent.parent.parent / "drafts"

PROMPT = """You are preparing the distribution pack for "Field Notes With Abhinav" — a newsletter by Microsoft MVP Abhinav Sharma for DevOps engineers, SREs, and platform teams.

Based on this newsletter content, generate ready-to-copy posts for each platform below.

NEWSLETTER:
{newsletter_content}

---

Generate the following. Be direct, no padding, no em-dashes.

## Twitter/X Thread
4 tweets posted as a thread. Each under 280 characters.
Tweet 1: bold hook that stops the scroll — one strong comparison or counterintuitive take
Tweet 2: expand the idea — one paragraph, one point
Tweet 3: the implication for platform teams — what this means operationally
Tweet 4: punchline + CTA with newsletter link placeholder [BEEHIIV_LINK] and tags #Kubernetes #DevOps #Azure #SRE #PlatformEngineering

## LinkedIn Post
Professional but direct. 150-200 words max.
- Open with the Field Note's strongest sentence
- 3-4 bullet points on what's in the issue
- End with: "Full issue → [BEEHIIV_LINK]"
- Add 5 hashtags at the bottom

## Dev.to
**Title:** (keyword-rich, under 60 chars)
**Description:** (2 sentences, under 160 chars, include "Kubernetes", "DevOps", "Azure")
**Tags:** (5 tags, comma separated)

## Hashnode
**Title:** (compelling, under 60 chars)
**Description:** (under 150 characters exactly — be precise)
**Tags:** (5 tags, comma separated)

## Microsoft Tech Community
**Title:** (professional, Azure-focused, under 70 chars)
**Opening paragraph:** (2-3 sentences introducing the issue, Azure-angle first)"""


def generate_distribution_pack(newsletter_content: str, issue_number: int, beehiiv_url: str) -> Path:
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-08-01-preview",
    )

    response = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[{"role": "user", "content": PROMPT.format(newsletter_content=newsletter_content)}],
        max_completion_tokens=2000,
        temperature=0.7,
    )

    content = response.choices[0].message.content
    content = content.replace("[BEEHIIV_LINK]", beehiiv_url)

    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_path = DRAFTS_DIR / f"{date_str}-distribution.md"

    header = f"# Distribution Pack — Field Notes Weekly #{issue_number}\n\n_{date_str}_\n\n---\n\n"
    out_path.write_text(header + content, encoding="utf-8")

    logger.info(f"Distribution pack saved: {out_path}")
    return out_path
