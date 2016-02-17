pyIsis: python wrapper for Avid Management Console
==================================================

pyIsis is a python wrapper that try to mimic Avis Isis Management Console
web service. It can manipulate workspaces, users, groups and permissions.
It can also manage snapshots, etc...


Installation
------------

From pypi:

.. code-block:: bash

  pip install pyIsis


From the source directory:

.. code-block:: bash

  git clone https://github.com/predat/pyIsis.git
  cd pyIsis
  pip install -r requirements.txt
  python setup.py install


TODO:
-----

- Test workspace creation and deletion on ISIS 7000 and 5500
- Handle user permissions correctly
- Add documentations
- Add examples
- More pythonic style to do things...

