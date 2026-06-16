import json


def parse_tool_args(content):
    """
    Parse tool arguments from JSON string or dict.
    """

    if isinstance(content, str):
        try:
            args = json.loads(content) if content.strip() else {}
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(str(e))

    elif isinstance(content, dict):
        args = content

    else:
        args = {}

    if (
        isinstance(args, dict)
        and len(args) == 1
        and "body" in args
        and isinstance(args["body"], dict)
        and "action" in args["body"]
    ):
        args = args["body"]

    return args
