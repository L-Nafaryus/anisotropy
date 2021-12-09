#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .models import __database__, __models__

database = __database__

class tables:
    pass

for model in __models__:
    setattr(tables, model.__name__, model)