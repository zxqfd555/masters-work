from masters.core.dataset import UnifiedDataset
from masters.solvers.rake import RAKEKeywordsExtractor


class DatasetAnalysisResult:

    def __init__(self, *, avg_tags, avg_tags_in_rake_candidates, avg_tags_in_rake_candidates_partial):
        self.avg_tags = avg_tags
        self.avg_tags_in_rake_candidates = avg_tags_in_rake_candidates
        self.avg_tags_in_rake_candidates_partial = avg_tags_in_rake_candidates_partial

    def as_dict(self):
        return {
            'avg_tags': self.avg_tags,
            'avg_tags_in_rake_candidates': self.avg_tags_in_rake_candidates,
            'avg_tags_in_rake_candidates_partial': self.avg_tags_in_rake_candidates_partial,
        }


class DatasetAnalyzer:

    def __init__(self, dataset):
        self._dataset = dataset

    @classmethod
    def from_filename(cls, source_fn):
        return cls(UnifiedDataset.from_filename(source_fn))

    def calculate_main_metrics(self):
        total_tags = sum([len(row.tags) for row in self._dataset.rows])

        avg_tags = total_tags / len(self._dataset.rows)
        avg_tags_in_rake_candidates = self._get_amt_in_rake_candidates() / len(self._dataset.rows)
        avg_tags_in_rake_candidates_partial = self._get_amt_in_rake_candidates(True) / len(self._dataset.rows)

        return DatasetAnalysisResult(
            avg_tags=avg_tags,
            avg_tags_in_rake_candidates=avg_tags_in_rake_candidates,
            avg_tags_in_rake_candidates_partial=avg_tags_in_rake_candidates_partial,
        )

    def _get_amt_in_rake_candidates(self, is_partial_match=False):
        total_matches = 0
        total_tags = 0
        for row in self._dataset.rows:
            text = row.content_clean
            candidates = RAKEKeywordsExtractor.generate_candidates(text)
            for tag in row.tags:
                if is_partial_match:
                    total_matches += 1 if DatasetAnalyzer._is_partially_matching_set(tag, candidates) else 0
                elif tag in candidates:
                    total_matches += 1
            total_tags += len(row.tags)

        return total_matches

    @staticmethod
    def _is_partially_matching_set(tag, candidates):
        tag_tokens = tag.split()
        for candidate in candidates:
            tokens = candidate.split()
            for token in tag_tokens:
                if token in tokens:
                    return True

        return False
