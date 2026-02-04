from loguru import logger

from google import genai
from google.genai.errors import ClientError, ServerError

from app.core.config import gemini_config_obj

client = genai.Client(api_key=gemini_config_obj.GEMINI_API_KEY)


class GeminiServiceError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


async def request_gemini(
        prompt: str = 'Привет, Gemini!',
        model_version: str = 'gemini-3-flash-preview'
) -> str:
    """
    :param prompt: prompt from user to ask from Gemini
     Example: 'Привет, Gemini!' as default or 'Hi, Gemini! What day is it today?'
    :param model_version: model name from Gemini API docs.
     Example: 'gemini-3-flash-preview' as default or 'gemini-2.5-flash-lite'

    :except ClientError: raises if model_version is incorrect
     or request has any other client-side trouble.
     Example: 'models/a is not found for API version v1beta, or is not
               supported for generateContent. Call ListModels to see the list of
               available models and their supported methods.'
    :except Exception: catches unexpected errors

    :return: Gemini's answer (response.text only)
    """

    if not gemini_config_obj.GEMINI_API_KEY:
        raise GeminiServiceError(500, "GEMINI_API_KEY is not configured")

    log = logger.bind(
        model=model_version,
        prompt_len=len(prompt),
    )

    log.info('Sending request to Gemini')

    try:
        response = await client.aio.models.generate_content(
            model=model_version,
            contents=prompt,
        )

    except ClientError as e:
        log.bind(
            error=e.message,
            error_code=e.code,
            error_type=type(e).__name__
        ).error(f'ClientError from Gemini! {e.code}: {e.message}')

        status_code = int(e.code) if getattr(e, "code", None) else 400
        raise GeminiServiceError(status_code, f'{e.code}: {e.message}')

    except ServerError as e:
        log.bind(
            error=str(e),
            error_code=e.code,
            error_type=type(e).__name__
        ).error(f'ServerError from Gemini! {e.code}: {e.message}')

        status_code = int(e.code) if getattr(e, "code", None) else 502
        raise GeminiServiceError(status_code, f'{e.code}: {e.message}')

    except Exception as e:
        # unknown or unexpected error
        log.bind(
            error=str(e),
            error_code=500,
            error_type=type(e).__name__
        ).error('Unexpected error while requesting Gemini!')

        raise GeminiServiceError(
            500,
            'Unknown error with 500 status code! We are working on it!',
        )

    log.info('Gemini response received successfully', answer_len=len(response.text or ""))
    return response.text
