import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class DuplicateDetection:

    def __init__(self, path, train_df, dupThreshold, classes):
        self.path = path
        self.train_df = train_df
        self.threshold = dupThreshold
        self.classes = classes

    @staticmethod
    def cosine_similarity(X, Y):
        dot = np.dot(X, Y)
        norma = np.linalg.norm(X)
        normb = np.linalg.norm(Y)
        cos = dot / (norma * normb)

        return cos

    # A naive algorithm for detecting duplicate documents
    def detect_duplicates(self):

        similarities = {}
        for label in self.classes:

            corpus = self.train_df.loc[self.train_df['Category'] == label]['Content'].values

            vectorizer = TfidfVectorizer(stop_words='english')
            X = vectorizer.fit_transform(corpus).toarray()

            # print(X.shape)

            for idx_i, i in enumerate(X):
                if i.any(axis=0) :
                    for idx_j in range(idx_i+1, len(X)):
                        j = X[idx_j]
                        if j.any(axis=0):
                            similarity = self.cosine_similarity(i, j)
                            if similarity >= self.threshold:
                                similarities[(idx_i,idx_j)] = similarity

        with open(self.path + "duplicatePairs.csv", "w") as f:
            sep = '\t'
            f.write('Document_ID1')
            f.write (sep)
            f.write('Document_ID2')
            f.write (sep)
            f.write('Similarity')
            f.write('\n')

            for x in similarities:
                f.write( str(x[0]) )
                f.write( sep )
                f.write( str(x[1]) )
                f.write( sep )
                f.write( str(similarities[x]) )
                f.write('\n')
                # print(str(x[0]) + "    " + str(x[1]) + "   " + str(similarities[x]) + "\n")
