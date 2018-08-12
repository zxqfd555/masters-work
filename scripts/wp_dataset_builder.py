import sys

from masters.crawlers.wordpress import download_dataset


if __name__ == '__main__':
    download_dataset(
        seeds_path=sys.argv[1],
        output_path=sys.argv[2],
        max_threads=int(sys.argv[3]),
    )
