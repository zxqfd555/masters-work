import requests

from masters.core.download import BasicDownloadTask
from .main_body import GenericPageProcessor


def create_example(input_url, output_fn):
    processor = GenericPageProcessor()

    raw_html = requests.get(input_url, timeout=10).text
    processor.feed(raw_html)
    result = BasicDownloadTask.remove_html_trace_simple(processor.get_main_body())

    result_header = """
    Demo of main body detection. The text below is the extracted main body by the proposed heuristic algorithm.\n
    Original: {}\n\n
    """.format(input_url)

    with open(output_fn, 'w', encoding='utf-8') as f:
        f.write(result_header + result)
