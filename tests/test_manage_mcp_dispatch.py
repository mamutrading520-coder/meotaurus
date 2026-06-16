import pytest
from unittest.mock import AsyncMock, patch

from src.agent_tools import ToolBlock
from src.tool_execution import execute_tool_block


@pytest.mark.asyncio
async def test_execute_tool_block_dispatches_manage_mcp():
    fake_result = {"status": "ok"}

    with patch(
        "services.platform.do_manage_mcp",
        new=AsyncMock(return_value=fake_result),
    ) as mock_mcp:

        desc, result = await execute_tool_block(
            ToolBlock("manage_mcp", '{"action":"list"}'),
            owner="admin",
        )

        assert desc == "manage_mcp"
        assert result == fake_result
        mock_mcp.assert_awaited_once()
