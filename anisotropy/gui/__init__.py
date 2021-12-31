# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from .main import app

if __name__ == "__main__":
    app.run_server(debug = True)