import requests
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
    retry_if_exception_type,
)
from loguru import logger
from typing import Literal


class SyncRequestMixin:
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=30, max=120),
        retry=retry_if_exception_type(Exception),
    )
    def sync_call(
        self,
        url: str,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        headers: dict | None = None,
        raise_on_exception: bool = True,
        raise_on_status_code: bool = False,
        params: dict | str | None = None,
        payload: list[dict] | dict | str | None = None,
        json_payload: dict | str | None = None,
    ) -> requests.Response:
        try:
            if headers is None:
                headers = {}

            if "Content-Type" not in headers:
                headers.update({"Content-Type": "application/json"})

            logger.info(
                f"SyncRequestMixin class was triggered. Parameters are; url: {url}, method: {method}, "
                f"headers: {headers}"
            )

            response = requests.request(
                url=url,
                data=payload,
                method=method,
                params=params,
                headers=headers,
                json=json_payload,
            )
            logger.info(
                f"SyncRequestMixin called to the {url}. status code is {response.status_code}"
            )
            if raise_on_status_code:
                response.raise_for_status()

            return response
        except Exception as e:
            logger.exception(
                f"Error occurred while sending request to {url}, error details are {str(e)}"
            )
            if raise_on_exception is True:
                raise e
