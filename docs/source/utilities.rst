Various utilities
=================

update_settings
-----------------

Django provides two utilities for settings overrides: `override_settings` and
`modify_settings`. The first allows you to simply override a value. The latter
– to manipulate lists (like `INSTALLED_APPS`). Djet supplements it with
`update_settings` that allows you to manipulate settings in form of
dictionaries. The arguments to `update_settings` should be dictionaries with
values to override in a dictionary. As with original django utilities it can be
used as a decorator or as a context manager::

    from djet.util import update_settings

    @update_settings(REST_FRAMEWORK={'PAGE_SIZE': 10})
    def test_with_pagination(self):
        # ...perform a test with PAGE_SIZE set to 10 and other REST_FRAMEWORK
        # params kept intact.


    def test_various_paginations(self):
        with update_settings(REST_FRAMEWORK={'PAGE_SIZE': 10}):
            # Perform the test with PAGE_SIZE set to 10
        # Perform the test with original PAGE_SIZE
        
