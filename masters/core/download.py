import json
import time
import os
import random
from abc import abstractmethod

import requests


class BasicDownloadTask:

    def __init__(self, url, rpt, n_attempts, timeout, backoff_rate, meta=None):
        self._url = url
        self._rpt = rpt
        self._n_attempts = n_attempts
        self._meta = meta

        self._timeout = timeout
        self._backoff_rate = backoff_rate

        self._output_path = os.getcwd()

    @classmethod
    def from_settings(cls, url, meta=None):
        with open('configs/downloader.json', 'r') as f:
            json_config = json.load(f)
        return cls(url, meta=meta, **json_config)

    @abstractmethod
    def execute(self):
        raise NotImplementedError

    def set_output_path(self, output_path):
        self._output_path = output_path

    def download_url(self, url):
        response = None
        timeout = self._timeout
        request_time_quant = 1.0 / self._rpt

        for attempt in range(self._n_attempts):
            time_before = time.time()
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
            except Exception:
                print('unable to load the url', self._url)
            else:
                break
            finally:
                time_spent = time.time() - time_before
                if time_spent < request_time_quant:
                    time.sleep(request_time_quant - time_spent)

                # exponential retry with random offset
                request_time_quant *= self._backoff_rate
                request_time_quant += random.uniform(0.0, 0.15)
        else:
            print('all load attempts have failed', self._url)
            return None

        return response

    def _remove_html_trace_simple(self, text):
        chars_lst = []
        nested_level = 0

        for ch in text:
            if ch == '<':
                nested_level += 1
            elif ch == '>':
                nested_level -= 1
            elif nested_level == 0:
                chars_lst.append(ch)
        result = ''.join(chars_lst)

        while '&#' in result:
            position = result.find('&#')
            length = result[position:].find(';') + 1
            result = result[:position] + ' ' + result[position + length:]

        result = self._clear_by_prefix(result, '\\u', 6, ' ')
        result = self._clear_by_prefix(result, '\\n', 2, ' ')
        result = self._clear_by_prefix(result, '\n', 1, ' ')
        result = self._clear_by_prefix(result, '&nbsp;', 5, ' ')

        return result

    def _clear_by_prefix(self, string, prefix, deletion_length, replacement_str):
        while prefix in string:
            position = string.find(prefix)
            string = string[:position] + replacement_str + string[position+deletion_length:]

        return string
