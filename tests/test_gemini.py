import json

import pytest
from unittest.mock import AsyncMock, patch

from google.genai.errors import ClientError

from app.services.gemini_client import request_gemini, GeminiServiceError


@pytest.mark.asyncio
@patch('app.services.gemini_client.client')
async def test_request_gemini_success(mock_client):
    mock_response = AsyncMock()
    mock_response.text = 'Hello from Gemini!'

    mock_client.aio.models.generate_content = AsyncMock(
        return_value=mock_response
    )

    result = await request_gemini('Hello')

    assert result == 'Hello from Gemini!'
    mock_client.aio.models.generate_content.assert_awaited_once()


@pytest.mark.asyncio
@patch('app.services.gemini_client.client')
async def test_request_gemini_client_error(mock_client):
    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=ClientError(
            code=400,
            response_json=json.loads('{"message": "Invalid model"}')

        )
    )

    with pytest.raises(GeminiServiceError) as exc:
        await request_gemini('Hello', 'invalid-model')
    assert exc.value.status_code == 400
    assert 'Invalid model' in exc.value.message


@pytest.mark.asyncio
@patch('app.services.gemini_client.client')
async def test_request_gemini_unexpected_error(mock_client):
    mock_client.aio.models.generate_content = AsyncMock(
        side_effect=RuntimeError('Boom')
    )

    with pytest.raises(GeminiServiceError) as exc:
        await request_gemini('Hello')
    assert exc.value.status_code == 500
