import time

import requests


TAG_POSTS_PATTERN = 'https://public-api.wordpress.com/rest/v1.1/read/tags/{}/posts'

REQUESTS_PER_SECOND = 5
N_ATTEMPTS = 3


class DownloadWorker:

    def __init__(self):
        

    def get_execute(self, tag):
        response = None
        url = TAG_POSTS_PATTERN.format(tag)
        for attempt in xrange(N_ATTEMPTS):
            time_before = time.time()
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
            except Exception:
                print 'unable to load url: {}'.format(url)
            else:
                break
            finally:
                time_spent = time.time() - time_before
                if time_spent < 1.0 / REQUESTS_PER_SECOND:
                    time.sleep(1.0 / REQUESTS_PER_SECOND - time_spent)
        else:
            print 'all attempts to load the url {} have failed'.format(url)

        response_json = response.json()
        for post in


if __name__ == '__main__':
    get_post('love')
