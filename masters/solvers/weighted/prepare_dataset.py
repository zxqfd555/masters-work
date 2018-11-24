from masters.core.dataset import UnifiedDataset


def prepare_wordpress_dataset(file_path):
    dataset = UnifiedDataset.from_filename(file_path)
    with open('wp.inputs.txt', 'w') as file_inputs, open('wp.titles.txt', 'w') as file_titles, open('wp.outputs.txt', 'w') as file_outputs:
        for row in dataset.rows:
            file_inputs.write(row.content_clean + '\n')
            file_titles.write(row.title_clean + '\n')

            clean_tags = []
            for tag in row.tags:
                if tag.startswith('#'):
                    clean_tags.append(tag[1:])
                else:
                    clean_tags.append(tag)

            file_outputs.write('\t'.join(clean_tags) + '\n')


if __name__ == '__main__':
    prepare_wordpress_dataset('~/Downloads/wordpress.json')
