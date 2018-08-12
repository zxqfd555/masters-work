import os
from multiprocessing.dummy import Pool as ThreadPool

from masters.core.download import BasicDownloadTask


TAG_POSTS_PATTERN = 'https://public-api.wordpress.com/rest/v1.1/read/tags/{}/posts'


class DownloadTask(BasicDownloadTask):

    @classmethod
    def from_settings(cls, tag, meta=None):
        url = TAG_POSTS_PATTERN.format(tag)
        return super().from_settings(
            url,
            meta={
                'tag': tag,
            }
        )

    def execute(self):
        response = self.download_url(self._url)
        if not response:
            return

        output_path = os.path.join(self._output_path, self._meta['tag'])
        with open(output_path, 'w') as f:
            f.write(response.text)


def download_dataset(seeds_path, output_path, max_threads):
    with open(seeds_path, 'r') as f:
        seeds = f.read().strip().split('\n')

    tasks = []
    for seed in seeds:
        task = DownloadTask.from_settings(seed)
        task.set_output_path(output_path)
        tasks.append(task)

    pool = ThreadPool(max_threads)
    pool.map(lambda t: t.execute(), tasks)
