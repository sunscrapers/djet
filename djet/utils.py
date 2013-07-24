def refresh(instance):
    return instance.__class__._default_manager.get(pk=instance.pk)