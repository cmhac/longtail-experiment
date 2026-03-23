"""ASGI entrypoint for the longtail backend API."""

from .app import create_app

app = create_app()
