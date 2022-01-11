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


###
#   Layout
##
layout = html.Div([
    #   Messages and timer
    dbc.Alert(
        id = "db_status", 
        duration = 10000, 
        dismissable = True, 
        is_open = False, 
        style = message 
    ),
    #dcc.Interval(id = "interval", interval = 1000, n_intervals = 0), 

    #   Query
    html.H2("Database"),
    html.Hr(),
    html.P("Query"),
    dcc.Textarea(id = "db_input", style = { "min-width": "100%"}),
    html.Br(),
    dbc.Button("Query", id = "query", style = minWidth),

    #   Output
    html.Hr(),
    html.P("Output"),
    DataTable(id = "db_output", columns = [], data = [], style_table = { "overflow": "scroll"}, style_cell={
                                    'textAlign': 'left',
                                    'width': '150px',
                                    'minWidth': '180px',
                                    'maxWidth': '180px',
                                    'whiteSpace': 'no-wrap',
                                    'overflow': 'hidden',
                                    'textOverflow': 'ellipsis',
                                }),
])


###
#   Callbacks
##
@app.callback(
    Output("db_output", "columns"),
    Output("db_output", "data"),
    Output("db_status", "children"), 
    Output("db_status", "is_open"), 
    Output("db_status", "color"),
    [ Input("query", "n_clicks") ],
    [ State("db_input", "value") ],
    prevent_initial_call = True
)
def db_query(clicks, db_input):
    from anisotropy.database import Database
    from peewee import OperationalError

    dbpath = os.path.join(os.environ["ANISOTROPY_CWD"], os.environ["ANISOTROPY_DB_FILE"])
    db = Database(path = dbpath)
    
    try:
        db.connect()
        cursor = db.execute_sql(db_input)
    
    except OperationalError as e:
        db.close()
        return None, None, str(e), True, "danger"
    
    else:
        columns = [ { "name": col[0], "id": col[0] } for col in cursor.description ]
        data = []

        for row in cursor.fetchall():
            item = {}

            for key, value in zip(columns, row):
                item[key["name"]] = value
            
            data.append(item)
        
        db.close()

        return columns, data, "", False, "success"