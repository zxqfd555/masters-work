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
            'avg_tags_in_rake_candidates': self.avg_tags_in_rake_candidates.as_dict(),
            'avg_tags_in_rake_candidates_partial': self.avg_tags_in_rake_candidates_partial.as_dict(),
        }


class RAKEMatchingResult:

    def __init__(self, *, avg_tags_in_content, avg_tags_in_title):
        self.avg_tags_in_content = avg_tags_in_content
        self.avg_tags_in_title = avg_tags_in_title

    def normalize(self, dataset_size):
        self.avg_tags_in_title /= dataset_size
        self.avg_tags_in_content /= dataset_size
        return self

    def as_dict(self):
        return {
            'content': self.avg_tags_in_content,
            'title': self.avg_tags_in_title,
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
        avg_tags_in_rake_candidates = self._get_amt_in_rake_candidates().normalize(len(self._dataset.rows))
        avg_tags_in_rake_candidates_partial = self._get_amt_in_rake_candidates(True).normalize(len(self._dataset.rows))

        return DatasetAnalysisResult(
            avg_tags=avg_tags,
            avg_tags_in_rake_candidates=avg_tags_in_rake_candidates,
            avg_tags_in_rake_candidates_partial=avg_tags_in_rake_candidates_partial,
        )

    def _get_amt_in_rake_candidates(self, is_partial_match=False):

        def get_total_matches(model_tags, content):
            candidates = RAKEKeywordsExtractor.generate_candidates(content)
            total_matches = 0
            for tag in model_tags:
                if is_partial_match:
                    total_matches += 1 if DatasetAnalyzer._is_partially_matching_set(tag, candidates) else 0
                elif tag in candidates:
                    total_matches += 1
            return total_matches

        total_matches_title = 0
        total_matches_content = 0
        for row in self._dataset.rows:
            total_matches_content += get_total_matches(row.tags, row.content_clean)
            total_matches_title += get_total_matches(row.tags, row.title_clean)

        return RAKEMatchingResult(
            avg_tags_in_title=total_matches_title,
            avg_tags_in_content=total_matches_content,
        )

    @staticmethod
    def _is_partially_matching_set(tag, candidates):
        tag_tokens = tag.split()
        for candidate in candidates:
            tokens = candidate.split()
            for token in tag_tokens:
                if token in tokens:
                    return True

        return False
