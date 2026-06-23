import pytest
from unittest.mock import AsyncMock, patch

from src.tool_implementations import do_manage_settings


@pytest.mark.asyncio
async def test_manage_settings_wrapper_delegates_to_settings_service():
    expected = {"response": "ok", "exit_code": 0}

    with patch(
        "services.settings.management_service.do_manage_settings",
        new=AsyncMock(return_value=expected),
    ) as mock_manage:
        result = await do_manage_settings('{"action":"list"}', owner="admin")

    assert result == expected
    mock_manage.assert_awaited_once()

    args, kwargs = mock_manage.await_args
    assert args == ('{"action":"list"}', "admin")
    assert "parse_tool_args" in kwargs
    assert "logger_obj" in kwargs
