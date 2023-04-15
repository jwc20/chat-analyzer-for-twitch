import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


import ipfshttpclient as ipfs

import json

hashes = [
    "QmWuhT48hnMHsaMpoX6eKPwx4PVTUbiJvy3YmkHMx8NH6v",  # toxicity
    "QmQDS4wxcAG5fVqmyfuwMn2pSpM1XQRcgWG8Mem5cU2p6J",  # profanity
    "QmZaVmGwq5WnryXowJk18Dp5i8NtuPbcvhdMNdK5oBXRMe",  # hate speech
]

# TODO: create separate class for ipfs.


class ChatClassifier:

    def __init__(
        self,
        toxicity_hash=hashes[0],
        profanity_hash=hashes[1],
        hate_speech_hash=hashes[2],
    ):
        self._client = ipfs.connect("/ip4/127.0.0.1/tcp/5002")
        self.toxicity_hash = toxicity_hash
        self.profanity_hash = profanity_hash
        self.hate_speech_hash = hate_speech_hash
        self.vectorizer = CountVectorizer()
        self.classifier = MultinomialNB()
        self.train_data = None
        self.train_labels = None
        self.pipeline = Pipeline(
            [
                ("vectorizer", CountVectorizer()),
                ("tfidf", TfidfTransformer()),
                ("clf", MultinomialNB()),
            ]
        )
        self.train()

    def load_dataset(self, hash):
        dataset = self._client.get_json(hash)
        json_data = pd.read_json(json.dumps(dataset))
        return json_data

    def train(self):
        # TODO: train the model for profanity and hate speech.
        dataset = self.load_dataset(self.toxicity_hash)
        # print(dataset.head())
        self.pipeline.fit(dataset["text"], dataset["Is this text toxic?"])

    def classify(self, message):
        # predictions = self.pipeline.predict(["this is a toxic text", "this is not a toxic text"])
        predictions = self.pipeline.predict([message])[0]
        return predictions

    def get_result(self, message):
        classification = self.classify(message)
        # print(f"Classification: {classification}")
        if classification == "Toxic":
            return "toxic"
        else:
            return "non-toxic"

    def get_toxicity_likelihood(self, message):
        probabilities = self.pipeline.predict_proba([message])
        toxic_probability = probabilities[0][1]  # Assuming index 1 corresponds to the "Toxic" class
        toxic_percentage = round(toxic_probability * 100, 1)
        return toxic_percentage


    def ipfs_close(self):
        self._client.close()


# if __name__ == "__main__":
#     classifier = ChatClassifier()
#     message = "this is a toxic text"
#     message = "FUCK YOU"
#     result = classifier.get_result(message)
#     print(f"The message '{message}' is {result}.")
#     classifier.ipfs_close()
