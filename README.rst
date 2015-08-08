Rigidity
========

.. image:: https://travis-ci.org/austinhartzheim/rigidity.svg?branch=master
   :target: https://travis-ci.org/austinhartzheim/rigidity
.. image:: https://coveralls.io/repos/austinhartzheim/rigidity/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/austinhartzheim/rigidity?branch=master 


Rigidity is a simple wrapper to Python's built-in `csv` module that allows for validation and correction of data being read or written with the `csv` module.

This module allows you to easily construct validation and correction rulesets to be applied automatically while preserving the `csv` interface. In other words, you can easily upgrade old code to better adhere to new output styles, or allow new code to better parse old files.

Examples
--------
Here is asimple example of validating UPC codes and ensuring their uniqueness::

   import rigidity
   
   rules = [
       [rigidity.rules.UpcA(strict=True),
        rigidity.rules.Unique()]
   ]
   r = rigidity.Rigidity(reader, rules)
   
   for row in r:
       print(row[0])

An explanation of this code and more documentation is available on `Read The Docs`_.

.. _Read The Docs: https://rigidity.readthedocs.org/en/latest/

Installing
----------
We are on `PyPI`_, so you can install us with `pip`::

   sudo pip3 install rigidity

.. _PyPI: https://pypi.python.org/pypi/rigidity/

Running Tests
-------------
You can easily run our unit tests at any time with Python's nosetests. If you also want to see test coverage, run this command.

   nosetests --with-coverage --cover-package=rigidity
