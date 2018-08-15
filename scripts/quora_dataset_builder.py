import sys

from masters.crawlers.quora import create_dataset


if __name__ == '__main__':
    create_dataset(
        n_articles=int(sys.argv[1]),
        n_workers=int(sys.argv[2]),
        seeds_filename=sys.argv[3],
        results_dir=sys.argv[4],
    )
