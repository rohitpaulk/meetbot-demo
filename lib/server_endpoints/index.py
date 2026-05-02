from __future__ import annotations

from pathlib import Path

from aiohttp import web
from jinja2 import Environment, FileSystemLoader, select_autoescape

MEETING_URL = "https://meet.google.com/non-sdhm-att"
TEMPLATES_DIR = Path(__file__).parents[1] / "templates"

_jinja = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(("html", "jinja")),
)


def render_index(status_message: str | None = None, status_kind: str = "success") -> web.Response:
    template = _jinja.get_template("index.html.jinja")
    html = template.render(
        title="Meetbot Demo",
        meeting_url=MEETING_URL,
        status_message=status_message,
        status_kind=status_kind,
    )

    return web.Response(text=html, content_type="text/html")


async def handle_index(_: web.Request) -> web.Response:
    return render_index()
