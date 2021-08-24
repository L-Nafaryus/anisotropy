Usefull command for making images
=================================

.. code-block:: python

    from peewee_erd import draw
    draw(["anisotropy/core/models.py"], "docs/source/static/er-diagram.svg", "#333333", "#eeeeee", 12, False, False)

.. code-block:: bash
    
    pydeps anisotropy --max-bacon 2 --cluster -o docs/source/static/deps.svg --noshow
