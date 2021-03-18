#!/usr/bin/env python
# -*- coding: utf-8 -*-

import salome

def hasDesktop() -> bool:
    return salome.sg.hasDesktop()

def execute():
    pass
