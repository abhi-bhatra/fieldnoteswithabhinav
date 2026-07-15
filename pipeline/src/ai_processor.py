import logging
import os

from openai import AzureOpenAI

from .rss_fetcher import Article

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are writing Field Notes Weekly — a newsletter by Abhinav Sharma (Microsoft MVP, Senior DevOps and Platform Engineer) for DevOps engineers, SREs, and platform engineers.

Voice: precise, dry, slightly wry. No hype. Lead with what matters. Skip filler.
Rules:
- No em-dashes
- No superlatives ("exciting", "game-changing", "revolutionary")
- No padding ("In today's fast-paced world...")
- Write like someone who operates real infrastructure daily and has no patience for marketing copy
- Links go inline: [Title](URL)"""

USER_PROMPT_TEMPLATE = """Here are this week's articles from Azure, Kubernetes, and DevOps sources:

{articles_block}

Write Field Notes Weekly Issue #{issue_number} with these three sections:

## Field Note
A short (3-4 sentences) personal observation or pattern you've noticed this week in platform engineering or DevOps. Ground it in one of the stories above or a broader operational trend. First person, direct.

## This Week's Reads
Pick the 5-7 most signal-rich stories from the list. For each item:
- **[Story Title](URL)** `source`
  2-3 sentences on what it is.
  **Why it matters:** one sentence, no padding.

## One to Watch
A single item — a PR, RFC, incident report, release, or tool — that most engineers will miss this week but shouldn't. One short paragraph explaining why you'd flag it.

Format in clean Markdown. Nothing else."""


def generate_newsletter(articles: list[Article], issue_number: int) -> dict:
    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version="2024-08-01-preview",
    )

    articles_block = "\n\n".join(
        f"Source: {a.source}\nTitle: {a.title}\nURL: {a.url}\nSummary: {a.summary}"
        for a in articles[:15]
    )

    response = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(
                articles_block=articles_block,
                issue_number=issue_number,
            )},
        ],
        max_tokens=2000,
        temperature=0.7,
    )

    content = response.choices[0].message.content
    title = f"Field Notes Weekly #{issue_number}"

    logger.info(f"Generated newsletter ({len(content)} chars)")
    return {"title": title, "content_markdown": content}
