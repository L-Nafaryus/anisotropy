
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from . import (
    runner,
    settings,
    about
)
from .app import app
from .styles import *
import anisotropy

###
#   Layout
##
app.layout = html.Div([
    #   Location
    dcc.Location(id = "url", refresh = False), 

    #   Sidebar
    html.Div([
        #   Sidebar
        html.H2([html.Img(src = "/assets/simple.png", height = "150px")], style = logo),
        html.Hr(style = { "color": "#ffffff" }),
        dbc.Nav([
            dbc.NavLink("Runner", href = "/", active = "exact", style = white),
            dbc.NavLink("Settings", href = "/settings", active = "exact", style = white),
            dbc.NavLink("About", href = "/about", active = "exact", style = white),
        ], vertical = True, pills = True),
        
        #   Misc
        html.Hr(style = white),
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
        ], style = misc)
    ], style = sidebar),

    #   Content
    html.Div(id = "page-content", style = page),
], style = content)


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

    else:
        return runner.layout 

