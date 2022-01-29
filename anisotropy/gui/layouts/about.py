# -*- coding: utf-8 -*-

from dash import html

import anisotropy


###
#   Layout
##
layout = html.Div([
    html.H1(anisotropy.__name__),
    html.Hr(),
    html.P([
        "Author: {}".format(anisotropy.__author__),
        html.Br(),
        "License: {}".format(anisotropy.__license__),
        html.Br(),
        "Version: {}".format(anisotropy.__version__)
    ])
]) 
