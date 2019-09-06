from django.conf import settings
from django.test.utils import override_settings


class update_settings(override_settings):
    def enable(self):
        new_options = {}
        for k, v in self.options.items():
            if hasattr(settings, k):
                new_value = getattr(settings, k).copy()
                new_value.update(v)
            else:
                new_value = v
            new_options[k] = new_value
        self.options = new_options
        super(update_settings, self).enable()
