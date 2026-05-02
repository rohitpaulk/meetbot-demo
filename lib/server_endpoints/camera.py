from __future__ import annotations

from pathlib import Path

from aiohttp import web
from jinja2 import Environment, FileSystemLoader, select_autoescape

IMAGE_URL = "https://ca.slack-edge.com/T02UQK7R1QC-U07H9ETQW67-fa8609795b2b-512"
TEMPLATES_DIR = Path(__file__).parents[1] / "templates"

_jinja = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(("html", "jinja")),
)


async def handle_camera(_: web.Request) -> web.Response:
    template = _jinja.get_template("camera.html.jinja")
    html = template.render(
        title="Meetbot Video",
        image_url=IMAGE_URL,
        image_alt="Meetbot avatar",
        caption="Meetbot is here.",
    )

    return web.Response(text=html, content_type="text/html")
