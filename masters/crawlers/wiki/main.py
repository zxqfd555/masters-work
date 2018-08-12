import os
import uuid
from multiprocessing.dummy import Pool as ThreadPool

from masters.core.download import BasicDownloadTask


LANGUAGE_PATTERN = 'https://{}.wikipedia.org/wiki/Special:Random'


class DownloadTask(BasicDownloadTask):

    def execute(self):
        response = self.download_url(self._url)
        if response is None:
            return

        output_path = os.path.join(self._output_path, '{}.html'.format(uuid.uuid4()))
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)


def generate_tasks(template_task, num_articles):
    for _ in range(num_articles):
        yield template_task


def download_random_articles(language, num_articles, output_path, num_threads):
    url = LANGUAGE_PATTERN.format(language)

    model_task = DownloadTask.from_settings(url=url)
    model_task.set_output_path(output_path)
    tasks = generate_tasks(model_task, num_articles)

    pool = ThreadPool(num_threads)
    for _ in pool.imap_unordered(lambda x: x.execute(), tasks):
        pass
