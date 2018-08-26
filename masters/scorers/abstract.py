from abc import abstractmethod
from multiprocessing import Pool as ProcessPool


class AbstractScorer:

    def calculate_score_on_dataset(self, extractor, dataset):
        sum_scores = 0.0
        pool = ProcessPool(16)
        for score in pool.imap_unordered(self.make_calculate_score(extractor), dataset.rows):
            sum_scores += score
        return sum_scores / len(dataset.rows)

    def make_calculate_score(self, extractor):

        def func(dataset_row):
            model_keywords = dataset_row.tags
            extracted_keywords = extractor.extract_keywords(dataset_row.content_clean)
            return self.calculate_score(model_keywords, extracted_keywords)

        return func

    @abstractmethod
    def calculate_score(self, model_keywords, extracted_keywords):
        raise NotImplementedError
