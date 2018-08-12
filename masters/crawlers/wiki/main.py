import itertools
import json
import os
import uuid
from html.parser import HTMLParser
from multiprocessing.dummy import Pool as ThreadPool

from masters.core.download import BasicDownloadTask


LANGUAGE_PATTERN = 'https://{}.wikipedia.org/wiki/Special:Random'


class SimpleArticleBodyExtractor(HTMLParser):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._div_depth = 0
        self._exit_div_depth = None

        self._is_processing_main_body = False
        self._is_inside_table = False
        self._is_inside_title = False

        self._data_tokens_raw = []
        self._title = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = {}
        for attr in attrs:
            k, v = attr
            attrs_dict[k] = v
        attrs = attrs_dict

        if tag == 'div':
            self._div_depth += 1
            if attrs.get('class') == 'mw-parser-output' and not self._is_processing_main_body:
                self._exit_div_depth = self._div_depth
                self._is_processing_main_body = True
        elif tag == 'table':
            self._is_inside_table = True
        elif tag == 'title':
            self._is_inside_title = True

        if self._is_processing_main_body and self._should_append_data():
            tag_tokens = ['<', tag]
            for k, v in attrs.items():
                tag_tokens.append(' {}="{}"'.format(k, v))
            tag_tokens.append('>')
            self._data_tokens_raw.append(''.join(tag_tokens))

    def handle_endtag(self, tag):
        if self._is_processing_main_body and self._should_append_data():
            self._data_tokens_raw.append('</{}>'.format(tag))

        if tag == 'div':
            if self._div_depth == self._exit_div_depth:
                self._is_processing_main_body = False
            self._div_depth -= 1
        elif tag == 'table':
            self._is_inside_table = False
        elif tag == 'title':
            self._is_inside_title = False

    def handle_data(self, data):
        if self._is_processing_main_body and self._should_append_data():
            self._data_tokens_raw.append(data)
        if self._is_inside_title:
            self._title = data

    def get_main_body(self):
        return ' '.join(self._data_tokens_raw)

    def get_title(self):
        return self._title

    def _should_append_data(self):
        return self._div_depth == self._exit_div_depth and not self._is_inside_table


class DownloadTask(BasicDownloadTask):

    def execute(self):
        response = self.download_url(self._url)
        if response is None:
            return

        parser = SimpleArticleBodyExtractor()
        parser.feed(response.text)
        title = parser.get_title()
        main_body = parser.get_main_body()

        result_json = {
            'title_raw': title,
            'title_clean': title,
            'content_raw': main_body,
            'content_clean': self._remove_html_trace_simple(main_body),
        }

        output_path = os.path.join(self._output_path, '{}.html'.format(uuid.uuid4()))
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result_json, f)


def download_random_articles(language, num_articles, output_path, num_threads):
    url = LANGUAGE_PATTERN.format(language)

    model_task = DownloadTask.from_settings(url=url)
    model_task.set_output_path(output_path)
    tasks = itertools.repeat(model_task, num_articles)

    pool = ThreadPool(num_threads)
    for _ in pool.imap_unordered(lambda x: x.execute(), tasks):
        # Unwrap the result generator
        pass
