"""
Generates a branded social card (1200x630) for each newsletter issue.
Brand: charcoal background, amber accent, monospace — matches Field Notes aesthetic.
"""
import logging
import re
import textwrap
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Brand colours
# ---------------------------------------------------------------------------
BG_COLOR      = "#1C1C1C"   # charcoal
ACCENT_COLOR  = "#F5A623"   # amber
TEXT_PRIMARY  = "#F0EDE4"   # off-white
TEXT_MUTED    = "#888888"   # muted grey
DIVIDER_COLOR = "#333333"   # subtle divider

W, H = 1200, 630


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Try to load a monospace font; fall back to default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def _extract_topics(content_markdown: str, max_topics: int = 3) -> list[str]:
    """Pull story titles from the ## This Week's Reads section."""
    topics = re.findall(r"\*\*\[([^\]]+)\]", content_markdown)
    cleaned = []
    for t in topics[:max_topics]:
        t = t.strip()
        if len(t) > 55:
            t = t[:52] + "..."
        cleaned.append(t)
    return cleaned


def generate_banner(title: str, content_markdown: str, issue_number: int) -> Path:
    date_str  = datetime.now(timezone.utc).strftime("%B %d, %Y")
    topics    = _extract_topics(content_markdown)
    out_dir   = Path(__file__).parent.parent.parent / "drafts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path  = out_dir / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.png"

    img  = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # ---- subtle grid texture ------------------------------------------------
    for x in range(0, W, 40):
        draw.line([(x, 0), (x, H)], fill="#222222", width=1)
    for y in range(0, H, 40):
        draw.line([(0, y), (W, y)], fill="#222222", width=1)

    # ---- amber left accent bar ----------------------------------------------
    draw.rectangle([(60, 60), (68, H - 60)], fill=ACCENT_COLOR)

    # ---- channel name (top) -------------------------------------------------
    font_channel = _load_font(18)
    draw.text((92, 72), "FIELD NOTES WITH ABHINAV", font=font_channel, fill=ACCENT_COLOR)

    # ---- divider ------------------------------------------------------------
    draw.line([(92, 106), (W - 60, 106)], fill=DIVIDER_COLOR, width=1)

    # ---- issue label --------------------------------------------------------
    font_issue = _load_font(15)
    draw.text((92, 120), f"WEEKLY DIGEST  ·  ISSUE #{issue_number}  ·  {date_str.upper()}",
              font=font_issue, fill=TEXT_MUTED)

    # ---- main title ---------------------------------------------------------
    font_title = _load_font(54, bold=True)
    title_text = f"Field Notes\nWeekly #{issue_number}"
    draw.text((92, 160), title_text, font=font_title, fill=TEXT_PRIMARY)

    # ---- divider before topics ----------------------------------------------
    draw.line([(92, 360), (W - 60, 360)], fill=DIVIDER_COLOR, width=1)

    # ---- "THIS WEEK" label --------------------------------------------------
    font_label = _load_font(14)
    draw.text((92, 375), "THIS WEEK", font=font_label, fill=ACCENT_COLOR)

    # ---- topic bullets ------------------------------------------------------
    font_topic = _load_font(19)
    y_topic = 405
    for topic in topics:
        draw.text((92, y_topic), f"→  {topic}", font=font_topic, fill=TEXT_PRIMARY)
        y_topic += 46

    # ---- bottom URL ---------------------------------------------------------
    font_url = _load_font(15)
    draw.text((92, H - 72),
              "github.com/abhi-bhatra/fieldnoteswithabhinav",
              font=font_url, fill=TEXT_MUTED)

    # ---- amber bottom accent bar --------------------------------------------
    draw.rectangle([(0, H - 6), (W, H)], fill=ACCENT_COLOR)

    img.save(out_path, "PNG", optimize=True)
    logger.info(f"Banner saved: {out_path}")
    return out_path
