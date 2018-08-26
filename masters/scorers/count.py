from .abstract import AbstractScorer


class CountScorer(AbstractScorer):

    def calculate_score(self, model_keywords, extracted_keywords):
        extracted_keywords_set = set(extracted_keywords)
        result = 0
        for keyword in model_keywords:
            if keyword in extracted_keywords_set:
                result += 1
        return result
