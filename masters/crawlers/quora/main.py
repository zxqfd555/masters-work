from masters.crawlers.abstract import GeneralizedCrawler


class QuoraDatasetBuilder(GeneralizedCrawler):

    def _is_dataset_url(self, url):
        tokens = url.split('/')
        return len(tokens) == 4 and tokens[0] == 'www.quora.com' and tokens[2] == 'answer'

    def _is_expansion_url(self, url):
        tokens = url.split('/')
        is_profile_link = len(tokens) == 3 and tokens[0] == 'www.quora.com' and tokens[1] == 'profile'
        is_question_link = len(tokens) == 2 and len(tokens[1]) > 10
        return is_profile_link or is_question_link


def create_dataset(n_articles, n_workers, seeds_filename, results_dir):
    with open(seeds_filename, 'r') as f:
        seeds = f.read().strip().split('\n')

    builder = QuoraDatasetBuilder(
        n_articles=n_articles,
        n_workers=n_workers,
        seeds=seeds,
        results_dir=results_dir,
    )

    builder.start()
