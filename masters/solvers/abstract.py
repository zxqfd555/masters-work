from abc import abstractmethod


class AbstractKeywordsExtractor:

    @abstractmethod
    def extract_keywords(self, text):
        raise NotImplementedError
