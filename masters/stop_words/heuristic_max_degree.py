import json


def get_text_tokens(text, punctuations='.,:;', braces='()[]{}<>\'"|'):
    text = ' '.join(text.split('\n'))
    text = ' '.join(text.split('\t'))
    raw_tokens = text.lower().split()
    clean_tokens = []
    for token in raw_tokens:
        if not token:
            continue
        has_punctuation_after = token[-1] in punctuations
        token = token.strip(punctuations).strip(braces)
        if token:
            if has_punctuation_after and (not clean_tokens or clean_tokens[-1] != '.'):
                clean_tokens.append('.')
            clean_tokens.append(token)
    return clean_tokens
            


def extract_stop_words(text):
    tokens = get_text_tokens(text)
    bigrams = {}
    for token_idx in range(len(tokens)-1):
        second = tokens[token_idx]
        first = tokens[token_idx + 1]
        if first not in bigrams:
            bigrams[first] = {}
        if second not in bigrams[first]:
            bigrams[first][second] = 0
        bigrams[first][second] += 1

    stopword_candidates = []
    for token in bigrams:
        stopword_candidates.append([token, (-len(bigrams[token]), max(bigrams[token].values()))])
    stopword_candidates.sort(key=lambda x: x[-1])

    return stopword_candidates


if __name__ == '__main__':
    with open('sample.txt', 'r') as f:
        text = f.read()
    cand = extract_stop_words(text)
    for c in cand[:30]:
        print(c[0], c[1])


