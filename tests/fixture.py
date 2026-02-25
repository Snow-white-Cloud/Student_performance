import pytest
from unittest.mock import AsyncMock
import json

@pytest.fixture
async def mock_get_connect():
    def _make(return_data=None, js=[]):
        get_conn = AsyncMock()
        get_conn.__aenter__.return_value = mock_connect(return_data, js)
        get_conn.__aexit__.return_value = None
        return get_conn
    return _make


@pytest.fixture
async def mock_connect():
    def _make(return_data=None, js=[]):
        conn = AsyncMock()
        conn.executemany = AsyncMock()
        conn.fetch = AsyncMock()
        conn.fetch.return_value = return_data
        if not isinstance(js, str):
            js = json.dumps(js)
        conn.fetchval.return_value = js

        tr = AsyncMock()
        tr.__aenter__.return_value = None
        tr.__aexit__.return_value = None
        conn.transaction.return_value = tr

        return conn
    return _make

