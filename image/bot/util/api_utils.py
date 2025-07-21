import aiohttp
import os
import json
from dotenv import load_dotenv
load_dotenv()
from logging import Logger

BASE_URL = os.getenv("API_URL")

async def _get(logger: Logger, content: dict, endpoint: str = "/"):
    """
    Performs an asynchronous HTTP GET request to a specified API endpoint using `aiohttp`.

    The method creates a session with `aiohttp.ClientSession`, constructs the request
    URL using the provided endpoint, and sends a GET request along with JSON content 
    and headers. Logs operations and handles response statuses and errors appropriately.

    :param logger: Logger instance for logging request-related messages
    :type logger: Logger
    :param content: JSON data to be included in the GET request
    :type content: dict
    :param endpoint: API endpoint to which the GET request is sent (default is '/')
    :type endpoint: str
    :return: API response as a dictionary. If an error occurs, returns a dictionary
        containing an error message
    :rtype: dict
    """
    try:
        async with aiohttp.ClientSession() as session:
            get_url = f"{BASE_URL}{endpoint}"
            headers = {"Content-Type": "application/json"}
            logger.info(f"Trying GET to URL: {get_url}")

            async with session.get(get_url, json=content, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    logger.info(f"API response (GET): {response_data}")
                    return response_data
                elif response.status == 500:
                    status = response.status
                    text = await response.text()
                    logger.error(f"GET failed with status {status}: {text}")
                    return {"error": f"API returned status {status}: {text}"}
                else:
                    status = response.status
                    text = await response.text()
                    logger.error(f"GET failed with status {status}: {text}")
                    return {"error": f"API returned status {status}: {text}"}
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        return {"error": f"Failed to create session: {str(e)}"}


async def _post(logger: Logger, content: dict, endpoint: str = "/"):
    """
    Posts JSON content to a specified API endpoint using an asynchronous
    HTTP session.

    :param content: The JSON payload to send in the POST request.
    :type content: json
    :param endpoint: The endpoint path to append to the base URL for
        the POST request.
    :type endpoint: str
    :param logger: The logger instance used for logging actions and
        errors.
    :type logger: logging.Logger
    :return: The API response from the POST request, typically as a
        dictionary. If the request fails, a dictionary containing an 
        error field with the error description is returned.
    :rtype: dict
    """
    try:
        async with aiohttp.ClientSession() as session:
            post_url = f"{BASE_URL}{endpoint}"
            headers = {"Content-Type": "application/json"}
            logger.info(f"Trying POST to URL: {post_url}")
            
            async with session.post(post_url, json=content, headers=headers) as response:
                if response.status == 200:
                    response_data = await response.json()
                    logger.info(f"API response (POST): {response_data}")
                    return response_data
                elif response.status == 500:
                    status = response.status
                    text = await response.text()
                    logger.error(f"POST failed with status {status}: {text}")
                    return {"error": f"API returned status {status}: {text}"}
                else:
                    status = response.status
                    text = await response.text()
                    logger.error(f"POST failed with status {status}: {text}")
                    return {"error": f"API returned status {status}: {text}"}
    except Exception as e:
        logger.error(f"Session creation error: {e}")
        return {"error": f"Failed to create session: {str(e)}"}


async def query_post(prompt, llm, model, logger, show_thoughts=False):
    query_payload = {
        "content": prompt,
        "llm": llm,
        "model": model,
        "show_thoughts": show_thoughts
    }
    return await _post(content=query_payload, endpoint="/query", logger=logger)


async def health_get(logger, verbosity: int = 1):
    return await _get(content={}, endpoint=f"/health/{verbosity}", logger=logger)