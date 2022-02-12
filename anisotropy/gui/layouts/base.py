# -*- coding: utf-8 -*-

from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from . import (
    runner,
    settings,
    database,
    visualization,
    about
)
from ..app import app
from .. import styles

import anisotropy

###
#   Layout
##
layout = html.Div([
    #   Location
    dcc.Location(id = "url", refresh = False), 

    #   Sidebar
    html.Div([
        #   Sidebar
        html.H2([html.Img(src = "/assets/simple.png", height = "150px")], style = styles.logo),
        html.Hr(style = { "color": "#ffffff" }),
        dbc.Nav([
            dbc.NavLink("Runner", href = "/", active = "exact", style = styles.white),
            dbc.NavLink("Settings", href = "/settings", active = "exact", style = styles.white),
            dbc.NavLink("Database", href = "/database", active = "exact", style = styles.white),
            dbc.NavLink("Visualization", href = "/visualization", active = "exact", style = styles.white),
            dbc.NavLink("About", href = "/about", active = "exact", style = styles.white),
        ], vertical = True, pills = True),
        
        #   Misc
        html.Hr(style = styles.white),
        dbc.Container([
            dbc.Row([
                dbc.Col("v1.2.0"),
                dbc.Col(
                    html.A(
                        html.Img(src = "/assets/gh-light.png", height = "20px"), 
                        href = anisotropy.__repository__ 
                    )
                )
            ])
        ], style = styles.misc)
    ], style = styles.sidebar),

    #   Content
    html.Div(id = "page-content", style = styles.page),
], style = styles.content)


###
#   Callbacks
##
@app.callback(
    Output("page-content", "children"),
    [ Input("url", "pathname") ]
)
def displayPage(pathname):
    if pathname == "/settings":
        return settings.layout

    elif pathname == "/about":
        return about.layout

    elif pathname == "/database":
        return database.layout

    elif pathname == "/visualization":
        return visualization.layout

    else:
        return runner.layout 
