import json
import threading
import queue
import os
import uuid
from abc import abstractmethod

from masters.core.download import BasicDownloadTask
from masters.main_body.main_body import GenericPageProcessor


class CrawlerDownloadTask(BasicDownloadTask):

    class CrawlerDownloadTaskResult:

        def __init__(self, main_body_raw, main_body_clean, links, title):
            self._main_body_raw = main_body_raw
            self._main_body_clean = main_body_clean
            self._links = links
            self._title = title

        @property
        def main_body_raw(self):
            return self._main_body_raw

        @property
        def main_body_clean(self):
            return self._main_body_clean

        @property
        def links(self):
            return self._links

        @property
        def title(self):
            return self._title

    def execute(self):
        response = self.download_url(self._url)
        if not response:
            return

        processor = GenericPageProcessor()
        processor.feed(response.text)

        main_body = processor.get_main_body()
        return self.CrawlerDownloadTaskResult(
            main_body_raw=main_body,
            main_body_clean=self.remove_html_trace_simple(main_body),
            links=processor.get_links(),
            title=processor.get_title(),
        )


class Worker:

    def __init__(self, master, results_dir):
        self._master = master

        self._main_thread = threading.Thread(target=self._do_work)
        self._results_dir = results_dir

    def start(self):
        self._main_thread.start()

    def join(self):
        self._main_thread.join()

    def _do_work(self):
        while True:
            url_for_download = self._master.get_download_url()
            if url_for_download is None:
                break

            task = CrawlerDownloadTask.from_settings('http://' + url_for_download)
            result = task.execute()
            if result is None:
                continue

            if self._master.is_should_save_for_dataset(url_for_download):
                self._save_for_dataset(result)
                self._master.notify_url_saved(url_for_download)

            for link in result.links:
                if link.startswith('/'):
                    link = url_for_download.split('/')[0] + link
                self._master.process_connection(url_for_download, link)

    def _save_for_dataset(self, result):
        path = os.path.join(self._results_dir, str(uuid.uuid4()) + '.json')

        result_json = {
            'content_raw': result.main_body_raw,
            'content_clean': result.main_body_clean,
            'title_raw': result.title,
            'title_clean': result.title,
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(result_json, f)


class GeneralizedCrawler:

    def __init__(self, n_articles, n_workers, seeds, results_dir):
        self._n_articles = n_articles

        self._saved_dataset_urls = set()
        self._processed_urls = set()

        self._queue = queue.Queue()
        for seed in seeds:
            self._queue.put(self._cannonize(seed))

        self._workers = []
        for _ in range(n_workers):
            self._workers.append(Worker(self, results_dir))

    def is_should_save_for_dataset(self, url):
        url = self._cannonize(url)

        return (
            (len(self._saved_dataset_urls) < self._n_articles)
                and
            (self.is_dataset_url(url))
                and
            (url not in self._saved_dataset_urls)
        )

    def is_dataset_url(self, url):
        return self._is_dataset_url(self._cannonize(url))

    def is_expansion_url(self, url):
        return self._is_expansion_url(self._cannonize(url))

    def notify_url_saved(self, url):
        url = self._cannonize(url)
        assert self.is_dataset_url(url)
        self._saved_dataset_urls.add(url)

    def process_connection(self, source, destination):
        destination = self._cannonize(destination)
        if destination in self._processed_urls:
            return

        is_destionation_expansion_url = self.is_expansion_url(destination)
        is_destination_dataset_url = self.is_dataset_url(destination)
        if not is_destination_dataset_url and not is_destionation_expansion_url:
            return

        self._queue.put(destination)

    def get_download_url(self):
        if len(self._saved_dataset_urls) >= self._n_articles:
            print('sending shutdown signal to a worker due to reaching the required dataset size')
            return None

        try:
            task = self._queue.get(timeout=30)
            self._queue.task_done()
        except queue.Empty:
            print('sending shutdown signal to a worker due to empty queue')
            return None

        return task

    def start(self):
        for worker in self._workers:
            worker.start()
        for worker in self._workers:
            worker.join()

    def _cannonize(self, url):
        if url.startswith('http://'):
            url = url[len('http://'):]
        elif url.startswith('https://'):
            url = url[len('https://'):]

        if '#' in url:
            position = url.find('#')
            url = url[:position]

        return url

    @abstractmethod
    def _is_dataset_url(self, url):
        """
        Whether the content of the page with this URL should be included in the dataset or not.
        """
        raise NotImplementedError

    @abstractmethod
    def _is_expansion_url(self, url):
        """
        Whether the URL of the page should be added to the queue with the hope of expanding to the
        new dataset URLs.
        """
        raise NotImplementedError
