"""Settings services package."""

__all__ = ["do_manage_settings"]


def __getattr__(name):
    if name == "do_manage_settings":
        from .management_service import do_manage_settings

        return do_manage_settings

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
