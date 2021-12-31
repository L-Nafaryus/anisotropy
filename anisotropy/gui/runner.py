# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from dash.dash_table import DataTable
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import os

from .app import app
from .styles import *
from .utils import getSize


###
#   Layout
##
layout = html.Div([
    #   Messages and timer
    dbc.Alert(
        id = "status", 
        duration = 10000, 
        dismissable = True, 
        is_open = False, 
        style = message 
    ),
    dcc.Interval(id = "interval", interval = 1000, n_intervals = 0), 

    #   Runner
    html.H2("Runner"),
    html.Hr(),
    dbc.Button("Start", id = "start", color = "success", style = minWidth),
    dbc.Button("Stop", id = "stop", color = "danger", disabled = True, style = minWidth),

    #   Monitor
    html.H2("Monitor"),
    html.Hr(),
    html.P(id = "runner-status"),
    DataTable(id = "monitor", columns = [], data = [], style_table = table),

    #   Log
    html.H2("Log"),
    html.Hr(),
    dbc.Button("Delete", id = "delete", style = minWidth),
    dcc.Textarea(id = "logger", disabled = True, style = bigText)

])


###
#   Callbacks
##
@app.callback(
    Output("start", "active"),
    [ Input("start", "n_clicks") ],
    prevent_initial_call = True
)
def runnerStart(clicks):
    import subprocess

    command = [
        "anisotropy",
        "compute",
        "-v",
        "--path", "/tmp/anisotropy",
        "--conf", "anisotropy.toml",
        "--pid", "anisotropy.pid",
        "--logfile", "anisotropy.log"
    ]

    subprocess.run(
        command,
        start_new_session = True,
    )

    return True

@app.callback(
    Output("stop", "active"),
    [ Input("stop", "n_clicks") ],
    prevent_initial_call = True
)
def runnerStop(clicks):
    import psutil
    import signal

    pidpath = "/tmp/anisotropy/anisotropy.pid"

    try:
        pid = int(open(pidpath, "r").read())
        master = psutil.Process(pid)
    
    except (FileNotFoundError, psutil.NoSuchProcess):
        return True

    else:
        os.killpg(master.pid, signal.SIGTERM)

        return True



@app.callback(
    Output("monitor", "columns"),
    Output("monitor", "data"),
    Output("runner-status", "children"),
    Output("start", "disabled"),
    Output("stop", "disabled"),
    Output("delete", "disabled"),
    [ Input("interval", "n_intervals") ],
)
def monitorUpdate(intervals):
    import psutil

    pidpath = "/tmp/anisotropy/anisotropy.pid"
    processes = []

    try:
        pid = int(open(pidpath, "r").read())
        master = psutil.Process(pid)
    
    except (FileNotFoundError, psutil.NoSuchProcess) as e:
        return [], [], "Status: not running", False, True, False
    
    else:
        for process in [ master, *master.children() ]:
            created = psutil.time.localtime(process.create_time())
            processes.append({
                "name": process.name(),
                "pid": process.pid,
                "status": process.status(),
                "memory": getSize(process.memory_full_info().uss),
                "threads": process.num_threads(),
                "created": "{}:{}:{}".format(created.tm_hour, created.tm_min, created.tm_sec)
            })
        
        columns = [ { "name": col, "id": col } for col in processes[0].keys() ]

        return columns, processes, "Status: running", True, False, True

@app.callback(
    Output("logger", "value"),
    [ Input("interval", "n_intervals") ]
)
def logUpdate(intervals):
    logpath = "/tmp/anisotropy/anisotropy.log"

    if os.path.exists(logpath):
        with open(logpath, "r") as io:
            log = io.read()
        
        return log
    
    else:
        return "Not found"


@app.callback(
    Output("delete", "active"),
    [ Input("delete", "n_clicks") ]
)
def logDelete(clicks):
    logpath = "/tmp/anisotropy/anisotropy.log"

    if os.path.exists(logpath):
        os.remove(logpath)
    
    return True