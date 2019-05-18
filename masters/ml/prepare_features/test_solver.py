import sys

import pickle


total_correct = 0
clf = None
labels = []
X = []
y = []


def clear_buffers():
    global labels
    global X
    global y
    X = []
    y = []
    labels = []


def flush_text():
    global clf
    global total_correct
    probs_tmp = clf.predict_proba(X)
    probs = []
    for i in range(len(probs_tmp)):
        probs.append((probs_tmp[i][1], y[i]))
    probs.sort(key=lambda x: -x[0])
    keywords_to_output = min(10, len(probs))
    total_correct += sum([x[1] for x in probs[:keywords_to_output]])
    clear_buffers()


if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as f:
        clf = pickle.load(f)
    print(list(clf.coef_))

    with open('test.txt', 'r') as f:
        for line in f:
            tokens = [int(x) for x in line.strip().split()]
            label = tokens[-1]
            ground_truth = tokens[-2]
            features = tokens[:-2]
            if labels and labels[-1] != label:
                flush_text()

            labels.append(label)
            X.append(features)
            y.append(ground_truth)

    flush_text()

    print('Right guesses:', total_correct)
