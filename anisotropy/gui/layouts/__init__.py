# -*- coding: utf-8 -*-

from . import (
    runner,
    settings,
    database,
    visualization,
    about,
    base
)
from .base import app


runner = runner.layout
settings = settings.layout
database = database.layout
visualization = visualization.layout
about = about.layout
base = base.layout

__all__ = [
    "runner",
    "settings",
    "database",
    "visualization",
    "about",
    "base",
    "app"
]
