"""Scheduled task services package."""

__all__ = ["do_manage_tasks"]


def __getattr__(name):
    if name == "do_manage_tasks":
        from .management_service import do_manage_tasks

        return do_manage_tasks

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
