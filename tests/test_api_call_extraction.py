import pytest
from unittest.mock import AsyncMock, patch

from src.tool_implementations import do_api_call


@pytest.mark.asyncio
async def test_do_api_call_wrapper_delegates_to_api_call_service():
    expected = {"ok": True, "delegated": True}

    with patch(
        "services.api_calls.management_service.do_api_call",
        new=AsyncMock(return_value=expected),
    ) as mock_api_call:
        result = await do_api_call("sample input")

    assert result == expected
    mock_api_call.assert_awaited_once_with("sample input")
