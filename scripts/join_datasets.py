import json
import os
import sys


if __name__ == '__main__':
    small_datasets_folder = sys.argv[1]
    final_dataset_file = sys.argv[2]

    large_dataset_data = []

    for filename in os.listdir(small_datasets_folder):
        path = os.path.join(small_datasets_folder, filename)
        with open(path, 'r') as f:
            small_dataset_data = json.load(f)
        large_dataset_data += small_dataset_data

    with open(final_dataset_file, 'w') as f:
        json.dump(large_dataset_data, f)
