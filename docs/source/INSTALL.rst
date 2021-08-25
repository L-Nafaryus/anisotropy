Installation
============

Recommended way is to install a package in the virtual environment. 
Just create and activate python virtual environment:

.. code-block:: bash

    $ python -m venv env
    $ source env/bin/activate

and run pip inside (upgrade pip if you need):

.. code-block:: bash

    (env) $ python -m pip install --upgrade pip
    (env) $ python -m pip install .

External applications
---------------------

Anisotropy project requires ``Salome`` and ``OpenFOAM`` executables be ``PATH``.

1. For simple way you can use next commands (each time):

.. code-block:: bash

    $ export PATH="${PATH}:${HOME}/PATH/TO/SALOME/DIRECTORY"
    $ source "${HOME}/PATH/TO/OPENFOAM/DIRECTORY/etc/bashrc"

2. Or modify file ``conf/bashrc`` in project directory (example)

.. code-block:: bash

    export PATH="${PATH}:${HOME}/programs/salome/SALOME-9.7.0-MPI"
    source "${HOME}/programs/OpenFOAM/OpenFOAM-v2012/etc/bashrc"

and source it (each time):

.. code-block:: bash

    $ source conf/bashrc

3. The best way is modify file like in step 2 and append it to virtual environment activate script:

.. code-block:: bash

    $ cat conf/bashrc | tee -a env/bin/activate

So next time you just need to ``source env/bin/activate`` and you completely ready.

Building documentaion
---------------------

For building documentaion you must sure that all requirements installed.
Project uses ``Sphinx`` and ``make`` for building:

.. code-block:: bash

    $ source env/bin/activate
    (env) $ cd docs
    (env) $ make html


