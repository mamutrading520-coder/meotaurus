import pytest
from unittest.mock import AsyncMock, patch

from src.tool_implementations import do_search_hf_models


@pytest.mark.asyncio
async def test_search_hf_models_wrapper_delegates_to_model_search_service():
    expected = {"output": "ok", "models": [], "exit_code": 0}

    with patch(
        "services.model_management.search_service.do_search_hf_models",
        new=AsyncMock(return_value=expected),
    ) as mock_search:
        result = await do_search_hf_models('{"query":"qwen"}', owner="admin")

    assert result == expected
    mock_search.assert_awaited_once_with('{"query":"qwen"}', "admin")
