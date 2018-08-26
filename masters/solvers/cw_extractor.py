from .abstract import AbstractKeywordsExtractor
from .rake import RAKEKeywordsExtractor


class CandidateWeightedKeywordExtractor(AbstractKeywordsExtractor):

    def __init__(self):
        self._is_fit = False

        self._title_occurrence_weight = None
        self._occ_position_penalty = None
        self._text_occurrence_weight = None
        self._len2_sep_words_occ_weight = None
        self._len3_sep_words_occ_weight = None

    def fit(self, dataset):
        raise NotImplementedError

    def load(self, config):
        self._title_occurrence_weight = config['title_occurrence_weight']
        self._text_occurrence_weight = config['text_occurrence_weight']
        self._occ_position_penalty = config['occ_number_penalty']
        self._len2_sep_words_occ_weight = config['len2_sep_words_occ_weight']
        self._len3_sep_words_occ_weight = config['len3_sep_words_occ_weight']

        self._is_fit = True

    def extract_keywords(self, text):
        if not self._is_fit:
            raise RuntimeError('fit the extractor before extracting keywords')

        text = RAKEKeywordsExtractor.normalize_text(text)
        candidates = self._generate_weighted_candidates(text)
