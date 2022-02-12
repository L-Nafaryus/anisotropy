# -*- coding: utf-8 -*-

from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_vtk
import dash_vtk.utils
import vtk

import pathlib
from os import environ

from ..app import app
from .. import styles


class MeshRepresentation(object):
    def __init__(self, path):
        self.mesh = vtk.vtkXMLUnstructuredGridReader()
        self.mesh.SetFileName(path)
        self.mesh.Update()

        self.clip = False
        self.crinkle = False
        self.wireframe = True
        self.planeNormal = [0, 0, -1]
        self.planeOrigin = [0, 0, 1]

    def getRepresentation(self):
        if not self.clip:
            dataset = self.mesh.GetOutput()
        
        else:
            plane = vtk.vtkPlane()
            plane.SetNormal(self.planeNormal)
            plane.SetOrigin(self.planeOrigin)

            if self.crinkle:
                implfunc = vtk.vtkImplicitBoolean()
                implfunc.AddFunction(plane)
                implfunc.Modified()

                clipper = vtk.vtkExtractGeometry()
                clipper.SetInputConnection(self.mesh.GetOutputPort())
                clipper.SetImplicitFunction(implfunc)
                clipper.SetExtractInside(1)
                clipper.SetExtractOnlyBoundaryCells(0)
                clipper.SetExtractBoundaryCells(1)
                clipper.ExtractInsideOff()

            else:
                clipper = vtk.vtkTableBasedClipDataSet()
                clipper.SetInputData(self.mesh.GetOutput())
                clipper.SetClipFunction(plane)
                clipper.SetValue(0.0)
                clipper.GenerateClippedOutputOn()
            
            clipper.Update()
            dataset = clipper.GetOutput()

        representation = dash_vtk.GeometryRepresentation(
            id = "mesh-representation",
            children = [
                dash_vtk.Mesh(id = "mesh", state = dash_vtk.utils.to_mesh_state(dataset))
            ],
            property = { "edgeVisibility": self.wireframe }
        )

        return representation
        

def databaseColumns():
    from anisotropy.database import Database
    import re

    db = Database()
    idcol = re.compile(r"\s*_id")
    columns = []

    for table in db.tables:
        for column in table._meta.columns.keys():
            if not idcol.search(column):
                columns.append(column)
    
    return columns


###
#   Layout
##
controls = html.Div([
    html.P("Execution"),
    dcc.Input(id = "exec_id", type = "number", value = 0, min = 0, style = styles.minWidth),
    html.Br(),

    html.P("Structure"),
    dcc.Dropdown(
        id = "structure",
        options = [ { "label": v, "value": v } for v in [ "simple", "bodyCentered", "faceCentered" ] ],
        value = "simple",
        style = styles.minWidth
    ),
    html.Br(),
    
    html.P("Direction"),
    dcc.Dropdown(
        id = "direction",
        options = [ { "label": str(v), "value": str(v)} for v in [ [1., 0., 0.], [0., 0., 1.], [1., 1., 1.] ] ],
        value = str([1., 0., 0.]),
    ),
    html.Br(),
    
    html.P("Alpha"),
    dcc.Input(id = "alpha", type = "number", value = 0.01, min = 0.01, step = 0.01, style = styles.minWidth),
    html.Br(),

    html.P("Clip"),
    dbc.Checkbox(id = "clip", value = False),
    html.Br(),

    html.P("Crinkle"),
    dbc.Checkbox(id = "crinkle", value = False),
    html.Br(),

    html.P("Plane normal"),
    dcc.Input(id = "normal-x", type = "number", value = 0, style = { "width": "100px", "margin-bottom": "20px" }), 
    dcc.Input(id = "normal-y", type = "number", value = 0, style = { "width": "100px", "margin-bottom": "20px" }), 
    dcc.Input(id = "normal-z", type = "number", value = -1, style = { "width": "100px", "margin-bottom": "20px" }),
    html.Br(),

    html.P("Plane origin"),
    dcc.Input(id = "origin-x", type = "number", value = 0, style = { "width": "100px", "margin-bottom": "20px" }), 
    dcc.Input(id = "origin-y", type = "number", value = 0, style = { "width": "100px", "margin-bottom": "20px" }), 
    dcc.Input(id = "origin-z", type = "number", value = 1, style = { "width": "100px", "margin-bottom": "20px" }),
    html.Br(),

    html.P("Wireframe"),
    dbc.Checkbox(id = "wireframe", value = True),
    html.Br(),

    dbc.Button("Draw", id = "draw"),
])

plotcontrols = html.Div([
    html.P("Execution"),
    dcc.Input(id = "plot-exec_id", type = "number", value = 0, min = 0, style = styles.minWidth),
    html.Br(),

    html.P("Structure"),
    dcc.Dropdown(
        id = "plot-structure",
        options = [ 
            { "label": v, "value": v } 
            for v in [ "simple", "bodyCentered", "faceCentered" ] 
        ],
        value = "simple"
    ),
    html.Br(),
    
    html.P("Direction"),
    dcc.Dropdown(
        id = "plot-direction",
        options = [ 
            { "label": str(v), "value": str(v)} 
            for v in [ [1., 0., 0.], [0., 0., 1.], [1., 1., 1.], "all" ] 
        ],
        value = str([1., 0., 0.]),
    ),
    html.Br(),

    html.P("Data"),
    dcc.Dropdown(
        id = "plot-data",
        options = [ { "label": v, "value": v } for v in databaseColumns() ], 
        value = "porosity",
    ),
    html.Br(),

    dbc.Button("Draw", id = "plot-draw"),
])

layout = html.Div([
    html.H2("Plot"),
    html.Hr(),
    dbc.Container(
        fluid = True,
        children = [
            dbc.Row([
                dbc.Col(width = 4, children = plotcontrols, style = { "min-width": "350px" }),
                dbc.Col(
                    width = 8,
                    children = [
                        html.Div(id = "plot-output", style = { "width": "100%", "min-width": "800px" })
                    ],
                    style = { "min-width": "800px" }
                ),
            ], style = { "height": "100%"}),
        ]),
    html.Br(),

    html.H2("Mesh"),
    html.Hr(),
    dbc.Container(
        fluid = True,
        children = [
            dbc.Row([
                dbc.Col(width = 4, children = controls, style = { "min-width": "350px" }),
                dbc.Col(
                    width = 8,
                    children = [
                        html.Div(
                            id = "vtk-output", 
                            style = { "height": "800px", "width": "100%", "min-width": "800px" }
                        )
                    ],
                    style = { "min-width": "800px" }),
            ], style = { "height": "100%"}),
        ])
])


@app.callback(
    [ Output("plot-output", "children") ],
    [ Input("plot-draw", "n_clicks") ],
    [
        State("plot-exec_id", "value"),
        State("plot-structure", "value"),
        State("plot-direction", "value"),
        State("plot-data", "value"),
    ]
)
def plotDraw(clicks, execution, structure, direction, data):
    from peewee import JOIN
    from anisotropy.database import Database, tables
    import json
    from pandas import DataFrame
    import plotly.express as px

    path = pathlib.Path(environ["AP_CWD"], environ["AP_DB_FILE"])

    if not path.is_file():
        return [ "Database not found" ]
    
    db = Database(path)
    
    if not db.getExecution(execution):
        return [ "Execution not found" ]
    
    for model in db.tables:
        try:
            column = getattr(model, data)
        
        except AttributeError:
            pass

        else:
            break

    if direction == "all":
        select = (tables.Shape.alpha, column, tables.Shape.direction)
    
    else:
        select = (tables.Shape.alpha, column)

    query = (
        tables.Shape
        .select(*select)
        .join(tables.Execution, JOIN.LEFT_OUTER)
        .switch(tables.Shape)
        .join(tables.Mesh, JOIN.LEFT_OUTER)
        .switch(tables.Shape)
        # .join(tables.FlowOnephase, JOIN.LEFT_OUTER)
        # .switch(tables.Shape)
        .where(
            tables.Shape.exec_id == execution,
            tables.Shape.label == structure,
        )
    )

    if not direction == "all":
        query = query.where(tables.Shape.direction == json.loads(direction))

    with db:
        if query.exists():
            table = []
            for row in query.dicts():
                for k in row.keys():
                    if type(row[k]) == list:
                        row[k] = str(row[k])

                table.append(row)
        
        else:
            table = None
    
    if not table:
        return [ "Results not found" ]

    import plotly.io as plt_io

    plt_io.templates["custom_dark"] = plt_io.templates["plotly_dark"]

    plt_io.templates["custom_dark"]['layout']['paper_bgcolor'] = '#30404D'
    plt_io.templates["custom_dark"]['layout']['plot_bgcolor'] = '#30404D'

    plt_io.templates['custom_dark']['layout']['yaxis']['gridcolor'] = '#4f687d'
    plt_io.templates['custom_dark']['layout']['xaxis']['gridcolor'] = '#4f687d'
    
    fig = px.line(
        DataFrame(table), x = "alpha", y = data, title = structure, markers = True
    )

    if direction == "all":
        fig = px.line(
            DataFrame(table), x = "alpha", y = data, title = structure, markers = True, color = "direction"
        )

    fig.layout.template = "custom_dark"
    fig.update_xaxes(showline = True, linewidth = 1, linecolor = '#4f687d', mirror = True)
    fig.update_yaxes(showline = True, linewidth = 1, linecolor = '#4f687d', mirror = True)

    plot = dcc.Graph(
        figure = fig
    )

    return [ plot ]
        

@app.callback(
    [ Output("alpha", "min"), Output("alpha", "max") ],
    [ Input("structure", "value") ]
)
def alphaLimits(label):
    if label == "simple":
        return 0.01, 0.29
    
    elif label == "bodyCentered":
        return 0.01, 0.18

    elif label == "faceCentered":
        return 0.01, 0.13


@app.callback(
    [ Output("vtk-output", "children") ],
    [ Input("draw", "n_clicks") ],
    [
        State("exec_id", "value"),
        State("structure", "value"),
        State("direction", "value"),
        State("alpha", "value"),
        State("clip", "value"),
        State("crinkle", "value"),
        State("wireframe", "value"),
        State("normal-x", "value"),
        State("normal-y", "value"),
        State("normal-z", "value"),
        State("origin-x", "value"),
        State("origin-y", "value"),
        State("origin-z", "value"),
    ],
    prevent_initial_call = True
)
def meshDraw(clicks, execution, structure, direction, alpha, clip, crinkle, wireframe, normal_x, normal_y, normal_z, origin_x, origin_y, origin_z):
    import meshio
    
    path = pathlib.Path(environ["AP_CWD"], environ["AP_BUILD_DIR"])
    path /= "execution-{}".format(execution)
    path /= "{}-{}-{}".format(
        structure, 
        direction.replace(" ", ""),
        alpha
    )
    basemeshpath = path / "mesh.msh"
    meshpath = path / "mesh.vtu"

    if not basemeshpath.exists():
        return [ "Mesh not found" ]

    if not meshpath.exists() or not meshpath.is_file():
        meshold = meshio.read(basemeshpath)
        meshold.write(meshpath)

    meshrepr = MeshRepresentation(meshpath)
    meshrepr.clip = clip 
    meshrepr.crinkle = crinkle 
    meshrepr.wireframe = wireframe
    meshrepr.planeNormal = [ normal_x, normal_y, normal_z ]
    meshrepr.planeOrigin = [ origin_x, origin_y, origin_z ]
    view = dash_vtk.View([ meshrepr.getRepresentation() ])

    return [ view ] 
