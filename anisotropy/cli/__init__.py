# -*- coding: utf-8 -*-

from . import utils

from .cli import anisotropy_cli


__all__ = [
    "utils",
    "anisotropy_cli"
]


if __name__ == "__main__":
    anisotropy_cli()
