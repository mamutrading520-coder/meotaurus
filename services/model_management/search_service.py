"""Model search tool service.

This module owns the HuggingFace model search tool implementation.

The implementation was moved mechanically from src.tool_implementations.
Do not change behavior in this extraction commit.
"""

from typing import Dict, Optional

import httpx

from src.tool_implementations import _INTERNAL_BASE, _internal_headers, _parse_tool_args


async def do_search_hf_models(content: str, owner: Optional[str] = None) -> Dict:
    """Search HuggingFace via the cookbook /api/cookbook/hf-latest endpoint."""
    import httpx
    try:
        args = _parse_tool_args(content)
    except ValueError:
        return {"error": "Invalid JSON arguments", "exit_code": 1}
    query = args.get("query", "") or args.get("search", "")
    limit = args.get("limit", 10)
    params: Dict[str, str] = {}
    if query:
        params["search"] = query
    if limit:
        params["limit"] = str(limit)
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{_INTERNAL_BASE}/api/cookbook/hf-latest",
                                    params=params, headers=_internal_headers())
            data = resp.json()
        models = data.get("models") if isinstance(data, dict) else data
        if not models:
            return {"output": f"No models found for query: {query!r}", "exit_code": 0}
        lines = [f"Found {len(models)} model(s) for {query!r}:" if query else f"{len(models)} model(s):"]
        for m in models[:limit if isinstance(limit, int) else 10]:
            if isinstance(m, dict):
                name = m.get("repo_id") or m.get("modelId") or m.get("id") or "?"
                dl = m.get("downloads")
                size = m.get("size_gb") or m.get("needed_vram_gb")
                bits = []
                if size:
                    bits.append(f"~{size}GB")
                if dl:
                    bits.append(f"{dl} downloads")
                tail = f" ({', '.join(bits)})" if bits else ""
                lines.append(f"- {name}{tail}")
            else:
                lines.append(f"- {m}")
        return {"output": "\n".join(lines), "models": models, "exit_code": 0}
    except Exception as e:
        return {"error": str(e), "exit_code": 1}
