# -*- coding: utf-8 -*-

from dash.dash_table import DataTable
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
    #   Messages and timer
    dbc.Alert(
        id = "db_status", 
        duration = 10000, 
        dismissable = True, 
        is_open = False, 
        style = styles.message 
    ),
    # dcc.Interval(id = "interval", interval = 1000, n_intervals = 0), 

    #   Query
    html.H2("Database"),
    html.Hr(),
    html.P("Query"),
    dcc.Textarea(id = "db_input", style = { "min-width": "100%"}),
    html.Br(),
    dbc.Button("Query", id = "query", style = styles.minWidth),

    #   Output
    html.Hr(),
    html.P("Output"),
    DataTable(
        id = "db_output", 
        columns = [], 
        data = [], 
        style_table = { "overflow": "scroll"}, 
        style_cell = {
            'textAlign': 'left',
            'width': '150px',
            'minWidth': '180px',
            'maxWidth': '180px',
            'whiteSpace': 'no-wrap',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        }
    ),
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
    from anisotropy import database
    import peewee as pw

    path = pathlib.Path(environ["AP_CWD"], environ["AP_DB_FILE"])
    db = database.Database(path)
    
    try:
        db.connect()
        cursor = db.execute_sql(db_input)
    
    except pw.OperationalError as e:
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
