"""API call services package."""

__all__ = ["do_api_call"]


def __getattr__(name):
    if name == "do_api_call":
        from .management_service import do_api_call

        return do_api_call

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
