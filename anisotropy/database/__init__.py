#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .models import __models__
from .db import Database

class tables:
    pass

for model in __models__:
    setattr(tables, model.__name__, model)