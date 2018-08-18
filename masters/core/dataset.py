import json
import random


class UnifiedDatasetRow:

    def __init__(self, *, content_raw, content_clean, title_raw, title_clean, tags):
        self._content_raw = content_raw
        self._content_clean = content_clean
        self._title_raw = title_raw
        self._title_clean = title_clean
        self._tags = tags

    @classmethod
    def from_filename(cls, filename):
        with open(filename, 'r') as f:
            params = json.load(f)
        return cls(**params)

    @property
    def content_raw(self):
        return self._content_raw

    @property
    def content_clean(self):
        return self._content_clean

    @property
    def title_raw(self):
        return self._title_raw

    @property
    def title_clean(self):
        return self._title_clean

    @property
    def tags(self):
        return self._tags


class UnifiedDataset:

    def __init__(self, rows):
        self._rows = rows

    @classmethod
    def from_filename(cls, filename):
        with open(filename, 'r') as f:
            rows_raw = json.load(f)

        rows = []
        for row_raw in rows_raw:
            rows.append(UnifiedDatasetRow(**row_raw))

        return cls(rows)

    @property
    def rows(self):
        return self._rows

    def get_random_text_with_tags(self):
        # Believe it or not, pretty useful for debug
        row_index = random.randint(0, len(self._rows))

        formatted_output = """Random text with tags.
        Title: {}\n
        Text: {}\n
        Tags: {}
        """.format(self._rows[row_index].title_clean, self._rows[row_index].content_clean, str(self._rows[row_index].tags))

        return formatted_output
