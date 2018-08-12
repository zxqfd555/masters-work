import json
import time
from abc import abstractmethod

import requests


class BasicDownloadWorker:

    def __init__(self, url, rpt, n_attempts):
        self._url = url
        self._rpt = rpt
        self._n_attempts = n_attempts

    @classmethod
    def from_settings(cls, url):
        with open('config.json', 'r') as f:
            json_config = json.load(f)
        return cls(url, **json_config)

    def download_url(self, url):
        response = None
        for attempt in range(self._n_attempts):
            time_before = time.time()
            try:
                response = requests.get(url, timeout=1)
                response.raise_for_status()
            except Exception:
                print('unable to load the url', self._url)
            else:
                break
            finally:
                time_spent = time.time() - time_before
                if time_spent < 1.0 / self._rpt:
                    time.sleep(1.0 / self._rpt - time_spent)
        else:
            print('all load attempts have failed', self._url)
            return None

        return response

    @abstractmethod
    def execute(self):
        raise NotImplementedError
