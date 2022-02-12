# -*- coding: utf-8 -*-

from dash.dash_table import DataTable
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import pathlib
import os
from os import environ

from ..app import app
from .. import styles
from .. import utils


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
        style = styles.message 
    ),
    dcc.Interval(id = "interval", interval = 1000, n_intervals = 0), 

    #   Runner
    html.H2("Runner"),
    html.Hr(),
    html.P("Execution (leave zero for the latest)"),
    dcc.Input(id = "execution", type = "number", value = 0, min = 0, style = styles.minWidth),
    html.Br(),
    dbc.Button("Start", id = "start", color = "success", style = styles.minWidth),
    dbc.Button("Stop", id = "stop", color = "danger", disabled = True, style = styles.minWidth),

    #   Monitor
    html.H2("Monitor"),
    html.Hr(),
    html.P(id = "runner-status"),
    DataTable(id = "monitor", columns = [], data = [], style_table = styles.table),

    #   Log
    html.H2("Log"),
    html.Hr(),
    dbc.Button("Delete", id = "delete", style = styles.minWidth),
    dcc.Textarea(id = "logger", disabled = True, style = styles.bigText)

])


###
#   Callbacks
##
@app.callback(
    Output("start", "active"),
    [ Input("start", "n_clicks") ],
    [ State("execution", "value") ],
    prevent_initial_call = True
)
def runnerStart(clicks, execution):
    import subprocess

    command = [
        "anisotropy",
        "compute",
        "-v",
        "--path", environ["AP_CWD"],
        "--conf", environ["AP_CONF_FILE"],
        "--pid", "anisotropy.pid",
        "--logfile", environ["AP_LOG_FILE"],
    ]

    if execution > 0:
        command.extend([ "--exec-id", str(execution) ])

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

    pidpath = pathlib.Path(environ["AP_CWD"], "anisotropy.pid")

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

    pidpath = pathlib.Path(environ["AP_CWD"], "anisotropy.pid")
    processes = []

    try:
        pid = int(open(pidpath, "r").read())
        master = psutil.Process(pid)
    
    except (FileNotFoundError, psutil.NoSuchProcess):
        return [], [], "Status: not running", False, True, False
    
    else:
        for process in [ master, *master.children() ]:
            created = psutil.time.localtime(process.create_time())
            processes.append({
                "name": process.name(),
                "pid": process.pid,
                "status": process.status(),
                "memory": utils.getSize(process.memory_full_info().uss),
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
    logpath = pathlib.Path(environ["AP_CWD"], "anisotropy.log")

    if os.path.exists(logpath):
        with open(logpath, "r") as io:
            log = io.read()
        
        return log
    
    else:
        return "Not found"


@app.callback(
    Output("delete", "active"),
    [ Input("delete", "n_clicks") ],
    prevent_initial_call = True
)
def logDelete(clicks):
    logpath = pathlib.Path(environ["AP_CWD"], "anisotropy.log")

    if os.path.exists(logpath):
        os.remove(logpath)
    
    return True
