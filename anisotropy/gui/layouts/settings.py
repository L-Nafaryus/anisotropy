# -*- coding: utf-8 -*-

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import pathlib
from os import environ

from ..app import app
from .. import styles


###
#   Layout
##
layout = html.Div([
    #   Messages
    dbc.Alert(
        id = "status", 
        duration = 10000, 
        dismissable = True, 
        is_open = False, 
        style = styles.message 
    ),
    dbc.Alert(
        id = "general-status", 
        duration = 10000, 
        dismissable = True, 
        is_open = False, 
        style = styles.message 
    ),
    #   General
    html.H2("General"),
    html.Hr(),
    html.P("Path"),
    dcc.Input(id = "cwd", style = { "min-width": "500px" }),
    html.Br(),
    dbc.Button("Save general", id = "general-save", style = styles.minWidth),
    
    #   Options
    html.H2("Options"),
    html.Hr(),
    html.P("Nprocs"),
    dcc.Input(id = "nprocs", type = "number", style = styles.minWidth),
    html.P("Stage"),
    dcc.Dropdown(
        id = "stage",
        options = [ { "label": k, "value": k } for k in ["all", "shape", "mesh", "flow", "postProcess"] ],
        style = styles.minWidth 
    ),
    dbc.Button("Save", id = "submit", style = styles.minWidth),

    #   Cases
    html.H2("Cases"),
    html.Hr(),
    dcc.Textarea(id = "cases", style = styles.bigText),
])


###
#   Callbacks
##
@app.callback(
    Output("general-status", "children"), 
    Output("general-status", "is_open"), 
    Output("general-status", "color"),
    [ Input("general-save", "n_clicks") ],
    [ 
        State("cwd", "value"),
    ],
    prevent_initial_call = True
)
def generalSave(clicks, cwd):
    path = pathlib.Path(cwd)

    if not path.is_absolute():
        return "Cwd path must be absolute", True, "danger"
    
    environ["AP_CWD"] = str(path)

    return "General settings saved", True, "success"


@app.callback(
    Output("cwd", "value"),
    Output("nprocs", "value"),
    Output("stage", "value"),
    Output("cases", "value"),
    [ Input("url", "pathname") ]
)
def settingsLoad(pathname):
    from anisotropy.core import config as core_config
    import toml

    path = pathlib.Path(environ["AP_CWD"], environ["AP_CONF_FILE"])
    config = core_config.default_config()

    if path.exists():
        config.load(path)

    return environ["AP_CWD"], config["nprocs"], config["stage"], toml.dumps(config.content)


@app.callback(
    Output("status", "children"), 
    Output("status", "is_open"), 
    Output("status", "color"),
    [ Input("submit", "n_clicks") ],
    [ 
        State("nprocs", "value"),
        State("stage", "value"),
        State("cases", "value") 
    ],
    prevent_initial_call = True
)
def settingsSave(nclick, nprocs, stage, cases):
    from anisotropy.core import config as core_config
    import toml

    path = pathlib.Path(environ["AP_CWD"], environ["AP_CONF_FILE"])
    config = core_config.default_config()

    if path.exists():
        config.load(path) 

    config.update(
        nprocs = nprocs,
        stage = stage
    )
    
    try:
        config.content = toml.loads(cases)
        config.dump(path)

    except Exception as e:
        return str(e), True, "danger"
    
    else:
        return f"Saved to { path }", True, "success"
