import sys

from masters.crawlers.wiki import download_random_articles


if __name__ == '__main__':
    download_random_articles(
        language=sys.argv[1],
        num_articles=int(sys.argv[2]),
        output_path=sys.argv[3],
        num_threads=int(sys.argv[4]),
    )
