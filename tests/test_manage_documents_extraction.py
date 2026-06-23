import pytest
from unittest.mock import AsyncMock, patch

from src.tool_implementations import do_manage_documents


@pytest.mark.asyncio
async def test_manage_documents_wrapper_delegates_to_docs_service():
    expected = {"response": "ok", "exit_code": 0}

    with patch(
        "services.docs.management_service.do_manage_documents",
        new=AsyncMock(return_value=expected),
    ) as mock_manage:
        result = await do_manage_documents('{"action":"list"}', owner="admin")

    assert result == expected
    mock_manage.assert_awaited_once_with('{"action":"list"}', "admin")
