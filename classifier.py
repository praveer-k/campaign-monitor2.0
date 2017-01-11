import os, pickle, openpyxl, helper, sys
from statistics import mode
from progress.bar import IncrementalBar
# Parsing Algorithms
from nltk.corpus import stopwords
from nltk.corpus import twitter_samples
from nltk.tokenize import TweetTokenizer
# returns the most appropriate label for the given featureset -->
from nltk.classify import ClassifierI
# Training Algorithms
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC

path = sys.argv[1]
with open(path) as f:
    keys = f.readlines()
    KEYWORD1 = keys[0].rstrip()
    KEYWORD2 = keys[1].rstrip()
    SINCE    = keys[2].rstrip()
    UNTIL    = keys[3].rstrip()
    DBName   = keys[4].rstrip()
    COUNTRY  = keys[5].rstrip()

class Classifier(ClassifierI):
    def __init__(self, *args):
        self.__classifiers = list(args)
    def push(self, clf):
        self.__classifiers += [clf]
    # extend the functionality of "ClassifierI.classify()" function
    def classify(self, features):
        votes = []
        for c in self.__classifiers:
            v = c.classify(features)
            votes.append(v)
        winner = mode(votes)
        chosen_winner = votes.count(winner)
        confidence = round(float(chosen_winner)/float(len(votes))*100, 2)
        return winner, confidence

def write_header(worksheet, headers):
    for k in range(1, len(headers)+1):
        worksheet.cell(row=1, column=k, value=headers[k-1])
        worksheet.cell(row=1, column=k).font = openpyxl.styles.Font(bold=True)
    return 2

def sentiment(text, featuring_words):
    words = tokenizer.tokenize(text)
    words = [w.lower() for w in words if w.lower() not in stop_words]
    featureset = {}
    for w in featuring_words:
        featureset[w] = (w in words)
    return clfs.classify(featureset)

if __name__ == "__main__":
    KEYWORD = KEYWORD1 + " " + KEYWORD2
    # -----------------------------------------------------------
    dirpath = "data/"+DBName
    tokenizer  = TweetTokenizer()
    stop_words = stopwords.words("english")
    # -----------------------------------------------------------
    print("Loading Trained Classifiers ...")
    classifiers = ["MultinomialNB","BernoulliNB",
                   "LogisticRegression","SGDClassifier",
                   "SVC","NuSVC","LinearSVC" ]
    clfs = Classifier()
    for clf in classifiers:
        f = open("algos/"+clf+"classifier.pkl","rb")
        classifier = pickle.load(f)
        clfs.push(classifier)
        f.close()
    # -----------------------------------------------------------
    print("Loading featuring words (predictors) ...")
    f = open("algos/featuring_words.pkl", "rb")
    featuring_words = pickle.load(f)
    f.close()
    # -----------------------------------------------------------
    print("Analysing sentiments and confidence ...")
    f = open(dirpath+"/users.pkl", "rb")
    users = pickle.load(f)
    f.close()
    users  = helper.reverse_map(users)
    user_ids = list(sorted(users.keys()))
    # -----------------------------------------------------------
    var  = helper.get_variables("config/variables.yml")
    headers  = var["user"] + var["place"]
    headers += var["tweet"] + var["author"] + var["source"]
    headers += ["confidence", "category"]
    # -----------------------------------------------------------
    bar = IncrementalBar("Processing ", max=len(user_ids))
    # -----------------------------------------------------------
    workbook  = openpyxl.workbook.Workbook()
    worksheet = workbook.active
    worksheet.title = "DATA"
    row = write_header(worksheet, headers)
    # -----------------------------------------------------------
    for root, dirs, files in os.walk(dirpath):
        for afile in files:
            username = afile[1:len(afile)-4]   # remove "@"~~~".pkl"
            if username in user_ids:
                f = open(os.path.join(root,afile), "rb")
                statuses = pickle.load(f)
                f.close()
                user   = statuses["user"]
                tweets = statuses["timeline"]
                for tweet in tweets:
                    category, confidence = sentiment(tweet["text"], featuring_words)
                    col = 1
                    for colname in headers:
                        if colname in var["user"] or colname in var["place"]:
                            worksheet.cell(row=row, column=col, value=user[colname])
                        elif colname in var["tweet"] or colname in var["author"] or colname in var["source"]:
                            worksheet.cell(row=row, column=col, value=tweet[colname])
                        elif colname=="confidence":
                            worksheet.cell(row=row, column=col, value=confidence)
                        elif colname=="category":
                            worksheet.cell(row=row, column=col, value=category)
                        col += 1
                    row += 1
                bar.next()
    bar.finish()
    # -----------------------------------------------------------
    outpath = "public_html/output/"+DBName
    if not os.path.exists(outpath) and not os.path.isdir(outpath):
        print("Creating output folder ...")
        os.mkdir(outpath)
    workbook.save(outpath+"/"+DBName+".xlsx")
    print("Done.\nClassification Completed !!!")
