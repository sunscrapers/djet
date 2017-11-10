import django

if django.VERSION < (1, 6):
    from .test_testcases import *
    from .test_assertions import *
    from .test_files import *
    from .test_utils import *
    from .test_restframework import *
