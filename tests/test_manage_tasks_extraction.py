import pytest
from unittest.mock import AsyncMock, patch

from src.tool_implementations import do_manage_tasks


@pytest.mark.asyncio
async def test_manage_tasks_wrapper_delegates_to_tasks_service():
    expected = {"response": "ok", "exit_code": 0}

    with patch(
        "services.scheduled_tasks.management_service.do_manage_tasks",
        new=AsyncMock(return_value=expected),
    ) as mock_manage:
        result = await do_manage_tasks('{"action":"list"}', owner="admin")

    assert result == expected
    mock_manage.assert_awaited_once_with('{"action":"list"}', "admin")
