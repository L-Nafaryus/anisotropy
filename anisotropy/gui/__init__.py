# -*- coding: utf-8 -*-

from . import layouts
from .layouts import app


app.layout = layouts.base


def run(*args, **kwargs):
    app.run_server(*args, **kwargs)


if __name__ == "__main__":
    run(debug = True)
