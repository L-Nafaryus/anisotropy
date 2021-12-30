
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import os
from .app import app
from .styles import *


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
        style = message 
    ),

    #   General
    html.H2("General"),
    html.Hr(),
    html.P("Path: {}".format(os.environ.get("ANISOTROPY_CWD", ""))),
    dbc.Button("Save", id = "submit", style = minWidth),
    
    #   Options
    html.H2("Options"),
    html.Hr(),
    html.P("Nprocs"),
    dcc.Input(id = "nprocs", type = "number", style = minWidth),
    html.P("Stage"),
    dcc.Dropdown(
        id = "stage",
        options = [ { "label": k, "value": k } for k in ["all", "shape", "mesh", "flow", "postProcess"] ],
        style = minWidth 
    ),

    #   Cases
    html.H2("Cases"),
    html.Hr(),
    dcc.Textarea(id = "cases", style = bigText),
])


###
#   Callbacks
##
@app.callback(
    Output("nprocs", "value"),
    Output("stage", "value"),
    Output("cases", "value"),
    [ Input("url", "pathname") ]
)
def settingsLoad(pathname):
    from anisotropy.core.config import DefaultConfig
    import toml

    filepath = os.path.join(os.environ["ANISOTROPY_CWD"], os.environ["ANISOTROPY_CONF_FILE"])
    config = DefaultConfig()

    if os.path.exists(filepath):
        config.load(filepath)

    return config["nprocs"], config["stage"], toml.dumps(config.content)


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
    from anisotropy.core.config import DefaultConfig
    import toml

    filepath = os.path.join(os.environ["ANISOTROPY_CWD"], os.environ["ANISOTROPY_CONF_FILE"])
    config = DefaultConfig()

    if os.path.exists(filepath):
        config.load(filepath) 

    config.update(
        nprocs = nprocs,
        stage = stage
    )
    
    try:
        config.content = toml.loads(cases)
        config.dump(filepath)

    except Exception as e:
        return str(e), True, "danger"
    
    else:
        return f"Saved to { filepath }", True, "success"