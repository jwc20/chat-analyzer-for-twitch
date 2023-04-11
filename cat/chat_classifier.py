# import all the libraries needed to build a toxicity classifier
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import seaborn as sns
import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import classification_report

import ipfshttpclient as ipfs

import json

hashes = [
    "QmWuhT48hnMHsaMpoX6eKPwx4PVTUbiJvy3YmkHMx8NH6v", # toxicity
    "QmQDS4wxcAG5fVqmyfuwMn2pSpM1XQRcgWG8Mem5cU2p6J", # profanity
    "QmZaVmGwq5WnryXowJk18Dp5i8NtuPbcvhdMNdK5oBXRMe", # hate speech
]

# TODO: create separate class for ipfs.

class ChatClassifier:
    """
    Classify chat messages as toxic, profanity, hate speech, or highlighted.
    TODO:
        - get data from the ipfs node.
        - classify the chat messages.
        - send the result to the chat window.
    """

    def __init__(self, toxicity_hash=hashes[0], profanity_hash=hashes[1], hate_speech_hash=hashes[2]):
        self._client = ipfs.connect("/ip4/127.0.0.1/tcp/5002")
        self.toxicity_hash = toxicity_hash
        self.profanity_hash = profanity_hash
        self.hate_speech_hash = hate_speech_hash
        self.vectorizer = CountVectorizer() 
        self.classifier = MultinomialNB()
        self.train_data = None 
        self.train_labels = None 
        # self.train()

    def load_data(self, hash): 
        # data = self._client.cat(hash)
        data = self._client.get_json(hash)
        return data


    def preprocess(self):
        pass

    def train(self):
        pass

    def classify(self):
        pass

    def get_result(self):
        pass

    def ipfs_close(self):
        self._client.close()
        pass

if __name__ == "__main__":
    classifier = ChatClassifier()
    data_toxicity = classifier.load_data(classifier.toxicity_hash)
    toxicity_json = json.dumps(data_toxicity)
    toxicity = pd.read_json(toxicity_json)
    # print(toxicity)

    pipeline = Pipeline([ 
        ("vectorizer", CountVectorizer()), 
        ("tfidf", TfidfTransformer()),
        ("clf", MultinomialNB())
    ])

    pipeline.fit(toxicity["text"], toxicity["Is this text toxic?"])
    predictions = pipeline.predict(["this is a toxic text", "this is not a toxic text"])
    print(predictions)
