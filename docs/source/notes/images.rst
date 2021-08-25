Usefull command for making images
=================================

For database ER diagram (``peewee_erd``):

.. code-block:: python

    from peewee_erd import draw
    draw(["anisotropy/core/models.py"], "docs/source/static/er-diagram.svg", "#333333", "#eeeeee", 12, False, False)

For project structure (``pydeps``):

.. code-block:: bash
    
    pydeps anisotropy --max-bacon 2 --cluster -o docs/source/static/deps.svg -T svg --noshow
