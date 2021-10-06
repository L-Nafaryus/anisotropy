List of known issues
====================

* ``Click`` // can't hide subcommand from help, ``hidden = True`` doesn't work.
* ``ideasUnvToFoam`` // can't import mesh with '-case' flag (temporary used ``os.chdir``).
* ``salome`` // removes commas from string list (example: "[1, 0, 0]") in the cli arguments.
* ``geompyBuilder`` // missing groups from father object in study tree.
* ``Anisotropy`` // writes ``Done`` status for failed operations (detected on mesh operations).
* ``Database`` // ``WHERE ..`` peewee operation error on update function with all control parameters (type, direction, theta) but fields are written to the database correctly.
* ``Database`` // awkward arguments and their order in the class init function.
* ``Mesh`` // outdated class.
* ``genmesh`` // awkward function, move precalculation parameters to Mesh class.
* ``Anisotropy`` // outdated functions for porosity and etc.
* ``Anisotropy`` // not sufficiently used variable ``env``.
* ``openfoam`` // outdated module, add functionality for FoamFile parsing, ``postProcess`` utility?.
* ``Database`` // add flexibility.