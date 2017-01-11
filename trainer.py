import pickle, random
# Parsing Algorithms
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.corpus import twitter_samples
from nltk.tokenize import TweetTokenizer
from nltk.stem.snowball import SnowballStemmer
# Port Between "nltk" And "sklearn"
from nltk.classify.scikitlearn import SklearnClassifier
from nltk.classify import accuracy
# Training Algorithms
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
# Tabulate in the Mark Down File
from tabulate import tabulate
from progress.bar import ChargingBar

class Tweets:
    def __init__(self, max_features=5000):
        self.__tokenizer  = TweetTokenizer()
        self.__stemmer    = SnowballStemmer("english")
        self.__stop_words = stopwords.words("english")
        self.__all_words  = []
        self.__document   = []
        self.__max_features = max_features # Predictors for the algorithm
        self.featuresets = []  # Publicly available data

    def push(self, tweets, category):
        for tweet in tweets:
            self.__document.append( (tweet, category))
            words = self.__tokenizer.tokenize(tweet)
            words = [w.lower() for w in words if w.lower() not in self.__stop_words]
            self.__all_words += words

    def pickle_featuring_words(self, path):
        wordFreq = FreqDist(self.__all_words)
        featuring_words = list(wordFreq.keys())[:self.__max_features]
        f = open(path, "wb")
        pickle.dump(featuring_words, f)
        f.close()

    def create_feature_sets(self):
        wordFreq = FreqDist(self.__all_words)
        featuring_words = list(wordFreq.keys())[:self.__max_features]
        self.featuresets = []
        for text, category in self.__document:
            words = self.__tokenizer.tokenize(text)
            words = [w.lower() for w in words if w.lower() not in self.__stop_words]
            words = [self.__stemmer.stem(w) for w in words]
            features = {}
            for w in featuring_words:
                features[w] = (w in words)
            self.featuresets += [(features, category)]

if __name__ == "__main__":
    print("Reading Data ...")
    pos_tweets = twitter_samples.strings("positive_tweets.json")
    neg_tweets = twitter_samples.strings("negative_tweets.json")
    data = Tweets(max_features=3000) # You can assign max_features i.e. no. of predictors
    data.push(pos_tweets, "pos")
    data.push(neg_tweets, "neg")
    print("Pickling Featuring Words (Predictors)... ")
    data.pickle_featuring_words("algos/featuring_words.pkl")
    print("Creating Feature Sets (Sample Sets)...")
    data.create_feature_sets()
    training_set = data.featuresets
    random.shuffle(training_set)
    n = len(training_set)
    p = len(training_set[0][0].keys())
    k = int(0.2*n)
    print("Total Sample (n) : ", n)
    print("Total Predictors (p) : ", p)
    print("No. of samples in training set : ",(n-k))
    print("No. of samples in test set : ",k)
    print("Training the System for Twitter sentiments ...")
    classifiers = [ # Naive Bayes ...
                    "MultinomialNB",
                    "BernoulliNB",
                    # Linear Models ...
                    "LogisticRegression",
                    "SGDClassifier",
                    # Support Vector Machines ...
                    "SVC",
                    "NuSVC",
                    "LinearSVC" ]

    table = [["classifier","accuracy"]]
    bar = ChargingBar("Processing", max=len(classifiers))
    bar.start()
    for clf in classifiers:
        classifier = SklearnClassifier(eval(clf+"()"))
        classifier.train(training_set[:(n-k)])
        table.append([clf, str(round(accuracy(classifier, training_set[(n-k):])*100,2))+"%"] )
        f = open("algos/"+clf+"classifier.pkl","wb")
        pickle.dump(classifier, f)
        f.close()
        bar.next()
    bar.finish()
    print( tabulate(table,headers="firstrow") )
    print("Training Completed !!!")
