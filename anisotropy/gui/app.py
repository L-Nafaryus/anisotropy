# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets = [ dbc.themes.LUX ])
app.title = "anisotropy"
app.config.update(
    update_title = None 
)