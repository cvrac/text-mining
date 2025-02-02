import pandas as pd
import logging
import os
import math

from classification.support_vector_machines import *
from classification.random_forests import *
from classification.custom_classifier import *

from word_cloud.word_cloud import *
from duplicates.duplicates_detection import *


class TextMining:

    def __init__(self, datasets, outputs, preprocess=False, wordclouds=False,
                 dup_threshold=None, classification=None, features=None, kfold=False, cache=False):
        self.datasets = datasets
        self.outputs = outputs
        self.preprocess = preprocess
        self.wordclouds = wordclouds
        self.dupThreshold = dup_threshold
        self.classification = classification
        self.features = features
        self.kfold = kfold
        self.cache = cache

        if self.cache:
            self.csv_train_file = datasets + '/' + 'processed_train_set.csv'
            self.csv_test_file = datasets + '/' + 'processed_test_set.csv'
        else:
            self.csv_train_file = datasets + '/' + 'train_set.csv'
            self.csv_test_file = datasets + '/' + 'test_set.csv'
        
        self.train_df = pd.read_csv(self.csv_train_file, sep='\t')
        self.test_df = pd.read_csv(self.csv_test_file, sep='\t') if not self.kfold else None

        self.classes = self.train_df.Category.unique()

        # define output directory names
        self.wordcloud_out_dir = outputs + '/' + 'wordcloud_out_dir/' if self.wordclouds else None
        self.duplicates_out_dir = outputs + '/' + 'duplicates_out_dir/' if self.dupThreshold else None
        self.classification_out_dir = outputs + '/' + 'classification_out_dir/' if self.classification else None

        if not os.path.exists(self.outputs):
            os.makedirs(self.outputs)

        if self.wordcloud_out_dir:
            if not os.path.exists(self.wordcloud_out_dir):
                os.makedirs(self.wordcloud_out_dir)

        if self.duplicates_out_dir:
            if not os.path.exists(self.duplicates_out_dir):
                os.makedirs(self.duplicates_out_dir)
       
        if self.classification_out_dir:
            if not os.path.exists(self.classification_out_dir):
                os.makedirs(self.classification_out_dir)

    def preprocess_data(self):
        print("..data preprocessing")
        preFilter = Preprocessor(transformation="lemmatization")

        # Preprocess training set
        processed_csv_train =  self.datasets + '/' + 'processed_train_set.csv'

        if not self.cache:
            if self.classification == "BEAT":
                print('Preprocess title')
                self.train_df = preFilter.text_transform(self.train_df, col='Title')
                self.train_df = preFilter.exclude_stop_words(self.train_df, col='Title')
            print('Preprocess content')
            self.train_df = preFilter.text_transform(self.train_df)
            self.train_df = preFilter.exclude_stop_words(self.train_df)
            preFilter.save_to_csv(self.train_df, processed_csv_train)

        if not self.kfold:  # Preprocess testing set
            processed_csv_test =  self.datasets + '/' + 'processed_test_set.csv'
            if not self.cache:
                if self.classification == "BEAT":
                    print('Preprocess title')
                    self.test_df = preFilter.text_transform(self.test_df, col='Title')
                    self.test_df = preFilter.exclude_stop_words(self.test_df, col='Title')
                if not self.cache:
                    print('Preprocess content')
                    self.test_df = preFilter.exclude_stop_words(self.test_df)
                    self.test_df = preFilter.text_transform(self.test_df)
                preFilter.save_to_csv(self.test_df, processed_csv_test)

    def generate_wordclouds(self):
        print("..generate wordclouds per category of the given dataset")
        wcGen = WordCloudGen(self.wordcloud_out_dir, self.csv_train_file, self.classes)
        wcGen.generate_wordclouds()

    def find_similar_docs(self):
        print("..find similar documents")
        dupDet = DuplicateDetection(self.duplicates_out_dir, self.train_df, self.dupThreshold, self.classes)
        dupDet.detect_duplicates()

    def run_classifiers(self):

        features = "Bow" if self.features is None else self.features
        print("..run " + str(self.classification) + " classifier with the selected features: " + str(features))

        if self.classification == 'SVM':
            clf = SupportVectorMachines
        elif self.classification == 'RF':
            clf = RandomForests
        elif self.classification == 'BEAT':
            print('...beat the benchmark pass')
            # print(self.train_df['Content'][0])
            # concat title X times to the content of the data
            self._concat()
            # print(self.train_df['Content'][0])
            clf = CustomClassifier
        else:
            logging.error('Unknown classifier "%s"', self.classification)

        classifier = clf(self.classification_out_dir, self.train_df, self.test_df, self.features)
        return classifier.run_kfold() if self.kfold else classifier.run_predict()        

    def _concat(self):
        # multiply string by value
        value = 5
        for index, row in self.train_df.iterrows():
            string_to_concat = ' ' + value * (str(self.train_df.at[index, 'Title']) + ' ')
            self.train_df.at[index, 'Content'] += string_to_concat

    def run(self):

        scores = None

        if not self.cache:
            if self.preprocess:
                self.preprocess_data()

        if self.wordclouds:
            self.generate_wordclouds()

        if self.dupThreshold:
            self.find_similar_docs()

        if self.classification:
                scores = self.run_classifiers()

        return scores


