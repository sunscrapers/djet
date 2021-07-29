Introduction
============

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

Installation
------------

Simply install using ``pip``:

.. code-block:: bash

    $ pip install djet

Requirements
------------

All of provided versions are validated via testing pipeline to ensure that
they are supported:

* **Python**: 3.6+
* **Django**: 2.2, 3.1+
* **Django REST Framework**: 3.11+ (optional)
