===============
ZTM api wrapper
===============

Fetch data from ZTM API


.. image:: https://img.shields.io/pypi/v/ztm.svg
        :target: https://pypi.python.org/pypi/ztm

.. image:: https://img.shields.io/travis/wooyek/ztm.svg
        :target: https://travis-ci.org/wooyek/ztm

.. image:: https://readthedocs.org/projects/ztm/badge/?version=latest
        :target: https://ztm.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
.. image:: https://coveralls.io/repos/github/wooyek/ztm/badge.svg?branch=develop
        :target: https://coveralls.io/github/wooyek/ztm?branch=develop
        :alt: Coveralls.io coverage

.. image:: https://codecov.io/gh/wooyek/ztm/branch/develop/graph/badge.svg
        :target: https://codecov.io/gh/wooyek/ztm
        :alt: CodeCov coverage

.. image:: https://api.codeclimate.com/v1/badges/0e7992f6259bc7fd1a1a/maintainability
        :target: https://codeclimate.com/github/wooyek/ztm/maintainability
        :alt: Maintainability

.. image:: https://img.shields.io/github/license/wooyek/ztm.svg
        :target: https://github.com/wooyek/ztm/blob/develop/LICENSE
        :alt: License

.. image:: https://img.shields.io/twitter/url/https/github.com/wooyek/ztm.svg?style=social
        :target: https://twitter.com/intent/tweet?text=Wow:&url=https://github.com/wooyek/ztm
        :alt: Tweet about this project

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
        :target: https://saythanks.io/to/wooyek



Features
--------

* Fetch GPS position and append to CSV file



Quickstart
----------

Install and run ZTM api wrapper::


    $ curl https://raw.githubusercontent.com/mitsuhiko/pipsi/master/get-pipsi.py | python
    $ pipsi install ztm
    $ ztm --apikey <APIKEY> fetch --line 150 --line 250
    $ cat ztm.csv


Running Tests
-------------

Does the code actually work?::

    $ git clone https://github.com/wooyek/ztm.git
    $ cd ztm
    $ curl https://raw.githubusercontent.com/mitsuhiko/pipsi/master/get-pipsi.py | python
    $ pipsi install pew
    $ pew new -p python3 -a $(pwd) $(pwd | xargs basename)
    $ pip install -r requirements/development.txt
    $ pipsi install tox
    $ tox


We recommend using pipsi_ for installing pew_ and tox_ but a legacy approach to creating virtualenv and installing requirements should also work.
Please install `requirements/development.txt` to setup virtual env for testing and development.


Credits
-------

This package was created with Cookiecutter_ and the `wooyek/cookiecutter-pylib`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`wooyek/cookiecutter-pylib`: https://github.com/wooyek/cookiecutter-pylib
.. _`pipsi`: https://github.com/mitsuhiko/pipsi
.. _`pew`: https://github.com/berdario/pew
.. _`tox`: https://tox.readthedocs.io/en/latest/
