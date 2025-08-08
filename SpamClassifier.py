import re
import math


class NBC:
    def __init__(self):
        self.spam_probabilities = {}
        self.nonspam_probabilities = {}
        self.spam_count = 0
        self.nonspam_count = 0


    def preprocess(self, X: list[str]) -> list[list[str]]:
        # Erasing all non-alphabetic characters and splitting by words
        preresult = []
        for sentence in X:
            preresult.append(re.sub(r'[^a-zA-Z]', ' ', sentence).lower().split())


        result = [[word for word in sentence if len(word) > 3] for sentence in preresult]

        return result


    # Gaussian smoothing
    def smoothing(self, X: list[list[str]]):
        for sentence in X:
            for word in sentence:
                self.spam_probabilities[word] = 1
                self.nonspam_probabilities[word] = 1



    def postprocess(self):
        nonspam_current = {}
        spam_current = {}
        for word in self.nonspam_probabilities:
            nonspam_current[word] = self.nonspam_probabilities[word] / len(self.nonspam_probabilities)
        for word in self.spam_probabilities:
            spam_current[word] = self.spam_probabilities[word] / len(self.spam_probabilities)

        self.nonspam_probabilities = nonspam_current
        self.spam_probabilities = spam_current


    def fit(self, X: list[str], y: list[int]):
        X_preprocessed = self.preprocess(X)
        self.smoothing(X_preprocessed)

        for sentence, cls in zip(X_preprocessed, y):
            if cls == 0:
                self.nonspam_count += 1
            else:
                self.spam_count += 1

            for word in sentence:
                if cls == 0:
                    self.nonspam_probabilities[word] += 1
                else:
                    self.spam_probabilities[word] += 1

        self.postprocess()


    def predict_proba(self, X: list[str]):
        nonspam = [self.nonspam_count / (self.spam_count + self.nonspam_count) for _ in range(len(X))]
        spam = [self.spam_count / (self.spam_count + self.nonspam_count) for _ in range(len(X))]
        X_preprocessed = self.preprocess(X)
        for i, obj in enumerate(X_preprocessed):
            for word in obj:
                if word in self.nonspam_probabilities:
                    nonspam[i] += math.log(self.nonspam_probabilities[word])
                if word in self.spam_probabilities:
                    spam[i] += math.log(self.spam_probabilities[word])

        return [[{0: nonspam[i], 1: spam[i]}] for i in range(len(X))]


    def predict(self, X: list[str]):
        nonspam = [self.nonspam_count / (self.spam_count + self.nonspam_count) for _ in range(len(X))]
        spam = [self.spam_count / (self.spam_count + self.nonspam_count) for _ in range(len(X))]
        X_preprocessed = self.preprocess(X)
        for i, obj in enumerate(X_preprocessed):
            for word in obj:
                if word in self.nonspam_probabilities:
                    nonspam[i] += math.log(self.nonspam_probabilities[word])
                if word in self.spam_probabilities:
                    spam[i] += math.log(self.spam_probabilities[word])
        return [0 if nonspam[i] > spam[i] else 1 for i in range(len(X))]



    def score(self, X_test: list[str], y_test: list[int]):
        predictions = self.predict(X_test)
        right_answers = 0
        wrong_answers = 0
        for i in range(len(X_test)):
            if predictions[i] == y_test[i]:
                right_answers += 1
            else:
                wrong_answers += 1
        return right_answers / (right_answers + wrong_answers)

    def get_dicts(self):
        return self.nonspam_probabilities, self.spam_probabilities
    def get_counters(self):
        return self.nonspam_count, self.spam_count

    def save_options(self):
        with open(f'options/spam_proba', 'w') as f:
            for word, proba in self.spam_probabilities.items():
                f.write(f"{word}:{proba},")
        with open(f'options/nonspam_proba', 'w') as f:
            for word, proba in self.nonspam_probabilities.items():
                f.write(f"{word}:{proba},")

        with open(f'options/spam_count', 'w') as f:
            f.write(str(self.spam_count))
        with open(f'options/nonspam_count', 'w') as f:
            f.write(str(self.nonspam_count))

    def dict_from_str_for_loading(self, content):
        spam_list = content.split(',')
        spam_keys = [obj[:obj.index(':')] for obj in spam_list]
        spam_values = [obj[obj.index(':') + 1:] for obj in spam_list]
        return {key: float(value) for key, value in zip(spam_keys, spam_values)}

    def load_options(self):
        with open('options/spam_proba', "r") as f:
            data = f.read()
            self.spam_probabilities = self.dict_from_str_for_loading(data[: len(data) - 1])
        with open('options/nonspam_proba', "r") as f:
            data = f.read()
            self.nonspam_probabilities = self.dict_from_str_for_loading(data[: len(data) - 1])

        with open('options/spam_count') as f:
            self.spam_count = int(f.read())
        with open('options/nonspam_count') as f:
            self.nonspam_count = int(f.read())