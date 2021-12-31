Installation
============

Base package
------------

Via virtual environment (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A recommended way is to install a package in the virtual environment.
Just create and activate python virtual environment:

.. code-block:: bash

    $ python -m venv env
    $ source env/bin/activate

and run pip inside (upgrade pip if you need):

.. code-block:: bash

    (env) $ python -m pip install --upgrade pip
    (env) $ python -m pip install .

User installation
~~~~~~~~~~~~~~~~~

Same but without the virtual environment:

.. code-block:: bash

    $ python -m pip install --upgrade pip
    $ python -m pip install .


External applications
---------------------

Anisotropy project requires ``Salome`` executable and ``OpenFOAM`` ``bashrc`` script be in ``PATH``.
You can choose your way by following one of the next step.

* You can use next commands directly (each time):

.. code-block:: bash

    $ export PATH="${HOME}/PATH/TO/SALOME/DIRECTORY:${PATH}"
    $ source "${HOME}/PATH/TO/OPENFOAM/DIRECTORY/etc/bashrc"

* Or modify file ``anisotropy/config/bashrc`` in project directory (example, ``bash``)

.. code-block:: bash

    export PATH="${HOME}/programs/salome/SALOME-9.7.0-MPI:${PATH}"
    source "${HOME}/programs/OpenFOAM/OpenFOAM-v2012/etc/bashrc"

and source it (each time):

.. code-block:: bash

    $ source anisotropy/config/bashrc

* The best way is to modify ``anisotropy/config/bashrc`` like in step 2 and append it to the virtual environment ``activate`` script:

.. code-block:: bash

    $ cat anisotropy/config/bashrc | tee -a env/bin/activate

So next time you just need to ``source env/bin/activate`` and you completely ready.

* You should add paths to ``~/.bashrc`` (``bash``) if you installed ``anisotropy`` in user path:

.. code-block:: bash

    $ cat anisotropy/config/bashrc | tee -a ~/.bashrc


Building documentaion
---------------------

For building a documentaion you should install a documentaion requirements:

.. code-block:: bash

    $ source env/bin/activate
    (env) $ python -m pip install "../anisotropy[documentaion]"


Then just run ``make`` with your best format option:

.. code-block:: bash

    (env) $ cd docs
    (env) $ make html

For more information about options you can read ``Sphinx`` documentaion or run ``make help``.
