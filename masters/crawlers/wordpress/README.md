# WordPress.com dataset builder

## Intro

A thank-you for the seeds list goes to "Education First".

They seeds themselves are taken from the page of 3000 most common words in English: https://www.ef.com/english-resources/english-vocabulary/top-3000-words/

## How to use

Anyone can repro the dataset construction for the required seeds.
The simplest way is (assuming you're in the repo root):

1. Copy wp_dataset_builder.py from scripts/ folder to the root.
2. Run (with Python 3): python wp_dataset_builder.py [path_to_seeds_file] [path_to_results_directory] [number_of_threads]
3. If you want to create one large JSON-file with the dataset, run join_datasets.py [path_to_results_directory] [path_to_output_file] from scripts/. The only reason I didn't do that in main script is that I didn't want a single download failure to screw up entire dataset creation process.

Keep in mind that from my expirience, that WP API is somehow slow and weak, so I don't recommend setting up much threads, you should also increase the number of retries is you experience lots of download failures.
On my PC with mediocre internet it took about 20 mins to download 10 articles on every seed from seeds.txt.

You can download the obtained dataset (28722 entries, 226 MB) here: TODO.