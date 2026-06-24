"""Notes services package."""

__all__ = ["do_manage_notes"]


def __getattr__(name):
    if name == "do_manage_notes":
        from .management_service import do_manage_notes

        return do_manage_notes

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
