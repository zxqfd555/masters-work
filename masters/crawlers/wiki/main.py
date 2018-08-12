import logging
import uuid
from multiprocessing.dummy import Pool as ThreadPool

import requests

from masters.core.worker import BasicDownloadWorker


LOGGER = logging.getLogger(__name__)

LANGUAGE_PATTERN = 'https://{}.wikipedia.org/wiki/Special:Random'


class DownloadWorker(BasicDownloadWorker):

    def execute(self):
        response = self.download_url(self._url)
        with open('results/{}.html'.format(uuid.uuid4()), 'w') as f:
            f.write(response.text.encode('utf-8'))


def generate_workers(template_worker, num_articles):
    for _ in xrange(num_articles):
        yield template_worker


def download_random_articles(language, num_articles, num_threads):
    url = LANGUAGE_PATTERN.format(language)
    workers = generate_workers(DownloadWorker.from_settings(url=url), num_articles)
    pool = ThreadPool(num_threads)
    pool.map(lambda x: x.execute(), workers)


if __name__ == '__main__':
    download_random_articles('en', 10000, 10)
