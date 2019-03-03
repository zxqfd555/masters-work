import random

import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression


def try_use_classifier(clf, prune_factor=1, model_name=None):
    X_train_new = []
    y_train_new = []
    for x, y in zip(X_train, y_train):
        if random.randint(1, prune_factor) == 1:
            X_train_new.append(x)
            y_train_new.append(y)

    print(len(X_train_new))
    clf.fit(X_train_new, y_train_new)
    if model_name:
        with open(model_name, 'wb') as f:
            pickle.dump(clf, f)

    predicted_classes = clf.predict(X_test)

    accuracy = 0.0
    for predicted, real in zip(predicted_classes, y_test):
        if predicted == real:
            accuracy += 1.0 / len(y_test)

    print(accuracy)

    predicted_probabilities_tmp = clf.predict_proba(X_test)
    predicted_probabilities = []
    for line in predicted_probabilities_tmp:
        predicted_probabilities.append(line[1])

    print(roc_auc_score(y_test, predicted_probabilities))


if __name__ == '__main__':
    X_train = []
    y_train = []
    X_test = []
    y_test = []

    with open('features-train.txt', 'r') as f:
        for line in f.readlines():
            tokens = [int(x) for x in line.strip().split()]
            X_train.append(tokens[:-1])
            y_train.append(tokens[-1])

    with open('features-test.txt', 'r') as f:
        for line in f.readlines():
            tokens = [int(x) for x in line.strip().split()]
            X_test.append(tokens[:-1])
            y_test.append(tokens[-1])
    """ 
    print('Trying RandomForestClassifier')
    clf = RandomForestClassifier(n_estimators=100)
    try_use_classifier(clf)

    print('Trying KNeighborsClassifier')
    clf = KNeighborsClassifier(n_neighbors=21)
    try_use_classifier(clf)
    """
    """
    print('Trying SVC')
    clf = SVC(probability=True)
    try_use_classifier(clf, prune_factor=61)
    """
    print('Trying LogisticRegression')
    clf = LogisticRegression(class_weight='balanced')
    try_use_classifier(clf, model_name='regression.clf')

