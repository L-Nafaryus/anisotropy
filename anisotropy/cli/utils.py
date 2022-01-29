# -*- coding: utf-8 -*-

import click
import ast
import logging


class LiteralOption(click.Option):
    def type_cast_value(self, ctx, value):
        try:
            return ast.literal_eval(value)

        except Exception:
            raise click.BadParameter(f"{ value } (Type error)")


class KeyValueOption(click.Option):
    def _convert(self, ctx, value):
        if not value:
            return {}

        if value.find("=") == -1:
            raise click.BadParameter(f"{ value } (Missed '=')")

        params = value.split("=")

        if not len(params) == 2:
            raise click.BadParameter(f"{ value } (Syntax error)")

        key, val = params[0].strip(), params[1].strip()

        if val[0].isalpha():
            val = f"'{ val }'"

        try:
            return { key: ast.literal_eval(val) }

        except Exception:
            raise click.BadParameter(f"{ value } (Type error)")

    def type_cast_value(self, ctx, value):
        if isinstance(value, list):
            return [ self._convert(ctx, val) for val in value ]

        else:
            return self._convert(ctx, value)


class CliListOption(click.Option):
    def _convert(self, ctx, value):
        if not value:
            return []

        output = [ val for val in value.split(",") ]
        
        if "" in output:
            raise click.BadParameter(f"{ value } (Trying to pass empty item)")

        return output

    def type_cast_value(self, ctx, value):
        if isinstance(value, list):
            return [ self._convert(ctx, val) for val in value ]

        else:
            return self._convert(ctx, value)

        
def verbose_level(level: int):
    return {
        0: logging.ERROR,
        1: logging.INFO,
        2: logging.DEBUG
    }.get(level, logging.ERROR)
