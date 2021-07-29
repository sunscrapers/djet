====
djet
====

.. image:: https://img.shields.io/pypi/v/djet.svg
  :target: https://pypi.org/project/djet

.. image:: https://img.shields.io/travis/sunscrapers/djet.svg
  :target: https://travis-ci.org/sunscrapers/djet

.. image:: https://img.shields.io/codecov/c/github/sunscrapers/djet.svg
  :target: https://codecov.io/gh/sunscrapers/djet

**Django Extended Tests** is a set of helpers for easy testing of Django apps.

Main features:

* easy unit testing of Django views (``ViewTestCase``)
* useful assertions provides as mixin classes:

  * response status codes (``StatusCodeAssertionsMixin``)
  * emails (``EmailAssertionsMixin``)
  * messages (``MessagesAssertionsMixin``)
  * model instances (``InstanceAssertionsMixin``)

* handy helpers for testing file-related code (``InMemoryStorageMixin`` and others)
* smooth integration with Django REST Framework authentication mechanism (``APIViewTestCase``)

Full documentation available on `read the docs <https://djet.readthedocs.io/en/latest/>`_.

Developed by `SUNSCRAPERS <http://sunscrapers.com>`_ with passion & patience.

Requirements
============

* **Python**: 3.6+
* **Django**: 2.2, 3.1+
* (optional) **Django REST Framework**: 3.11+

Installation
============

Simply install using ``pip``:

.. code-block:: bash

    $ pip install djet

Documentation
=============

Full documentation is available to study at
`read the docs <https://djet.readthedocs.io/en/latest/>`_
and in ``docs`` directory.
