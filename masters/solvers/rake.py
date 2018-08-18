from .abstract import AbstractKeywordsExtractor


class RAKEKeywordsExtractor(AbstractKeywordsExtractor):

    MAX_CANDIDATE_LENGTH = 3

    @classmethod
    def generate_candidates(cls, text):
        normalized_text_as_list = RAKEKeywordsExtractor.normalize_text(text, as_list=True)
        candidates = set()
        for start_index in range(len(normalized_text_as_list)):
            for candidate_length in range(1, cls.MAX_CANDIDATE_LENGTH+1):
                if start_index + candidate_length <= len(normalized_text_as_list):
                    candidates.add(
                        ' ' .join(normalized_text_as_list[start_index:start_index+candidate_length])
                    )
        return candidates

    @classmethod
    def normalize_text(cls, text, as_list=False):
        tokens = text.lower().split()
        normalized_tokens = []

        for token in tokens:
            current_token = ''
            last_char_is_word_part = (not tokens) or (tokens[-1].isalpha())

            for ch in token:
                if cls._is_word_part(ch):
                    current_token += ch
                    last_char_is_word_part = True
                else:
                    normalized_tokens.append(current_token)
                    current_token = ''

                    if last_char_is_word_part:
                        normalized_tokens.append('.')
                    last_char_is_word_part = False

            if current_token:
                normalized_tokens.append(current_token)

        if as_list:
            return normalized_tokens
        else:
            return ' '.join(normalized_tokens)

    @classmethod
    def _is_word_part(cls, ch):
        return ch.isalnum() or ch in ("'", '-')
