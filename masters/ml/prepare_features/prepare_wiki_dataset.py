import json


if __name__ == '__main__':
    with open('wiki.json', 'r') as f:
        dataset = json.load(f)
    with open('wiki.inputs.txt', 'w') as inputs, open('wiki.titles.txt', 'w') as titles, open('wiki.outputs.txt', 'w') as outputs:
        for line in dataset:
            inputs.write(line['content_clean'].encode('utf-8') + '\n')
            titles.write(line['title_clean'].encode('utf-8') + '\n')
            outputs.write('\t'.join(line['tags']).encode('utf-8') + '\n')

