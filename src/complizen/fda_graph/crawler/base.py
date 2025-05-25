import requests
from abc import ABC, abstractmethod
from ratelimit import sleep_and_retry, limits

from ..utils.request_mixin import SyncRequestMixin


class BaseCrawler(SyncRequestMixin, ABC):

    @sleep_and_retry
    @limits(calls=230, period=60)
    def call_api(self, url: str, method: str = "GET") -> requests.Response:
        response = self.sync_call(
            url=url,
            method=method,
            raise_on_exception=True,
            raise_on_status_code=False,
        )
        return response

    @abstractmethod
    def crawl(self):
        pass
