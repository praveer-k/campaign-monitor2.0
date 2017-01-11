import sys, pickle, os
import pylab as pl
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
import helper
from tabulate import tabulate
from progress.bar import ChargingBar

path = sys.argv[1]
with open(path) as f:
    keys = f.readlines()
    KEYWORD1 = keys[0].rstrip()
    KEYWORD2 = keys[1].rstrip()
    SINCE    = keys[2].rstrip()
    UNTIL    = keys[3].rstrip()
    DBName   = keys[4].rstrip()
    COUNTRY  = keys[5].rstrip()

figpath = "public_html/output/"+DBName
# -----------------------------------------------------------------------------
if not os.path.exists("data/"+DBName+"/model.pkl"):
    print("No data found...")
    exit()
# -----------------------------------------------------------------------------
f = open("data/"+DBName+"/model.pkl", "rb")
model = pickle.load(f)
f.close()
# -----------------------------------------------------------------------------
formula = model["formula"]
y = model["y"]
X = model["X"]
result = model["result"]

print("Diagnostics...")
# print(dir(result))
ypred = result.predict(X)
p = len(list(set(z.rstrip().lstrip() for x in formula.split("~")[1].split("+") for y in x.split(":") for z in y.split("*"))))
n = result.nobs
y = np.array(y["text"])
X = np.matrix(X)
H = X * np.linalg.inv(np.transpose(X) * X) * np.transpose(X)
h = np.diag(H)
rpear = result.resid_pearson
rdev = result.resid_dev
e = y-ypred
D = (rpear**2)*h/(2*(1-h))
cut_off = round(2*(p+1)/n, 5)
bar = ChargingBar("Processing", max=4)
bar.start()
pl.figure()
pl.grid(True)
pl.scatter(np.arange(len(rpear)), rpear)
pl.xlabel("Index")
pl.ylabel("Pearsons Residual")
pl.title("Index plot of pearsons residual")
pl.savefig(figpath+"/Fig13.png")
# pl.show()
pl.close()
bar.next()

pl.figure()
pl.grid(True)
pl.scatter(np.arange(len(rdev)), rdev)
pl.xlabel("Index")
pl.ylabel("Deviance Residual")
pl.title("Index plot of deviance residual")
pl.savefig(figpath+"/Fig14.png")
# pl.show()
pl.close()
bar.next()

pl.figure()
pl.grid(True)
pl.plot(np.arange(len(h)), h)
pl.axhline(y=cut_off, color="red")
pl.xlabel("Index")
pl.ylabel("Hat values")
pl.title("Plot for identifying cases of high leverage")
pl.savefig(figpath+"/Fig15.png")
# pl.show()
pl.close()
bar.next()

pl.figure()
pl.grid(True)
pl.plot(np.arange(len(D)), D)
pl.xlabel("Index")
pl.ylabel("Cooks Distance")
pl.title("Plot for identifying cases of high influence")
pl.savefig(figpath+"/Fig16.png")
# pl.show()
pl.close()
bar.next()
bar.finish()
# ------------------------------------------------------------------------------
high_leverage = list(np.where(h>cut_off)[0].tolist())
high_influence = list(np.where(D>10)[0].tolist())
diagnostics = pd.DataFrame({"y": y, "ypred": ypred, "e": e, "h": h, "rpear": rpear, "rdev": rdev, "D": D}, columns=["y","ypred","e","h","rpear","rdev","D"])
sample = []
for i in diagnostics.head().index:
    sample.append({"y": diagnostics.ix[i,"y"], "ypred": diagnostics.ix[i,"ypred"], "e": diagnostics.ix[i,"e"], "h": diagnostics.ix[i,"h"], "rpear": diagnostics.ix[i,"rpear"], "rdev": diagnostics.ix[i,"rdev"], "D": diagnostics.ix[i,"D"]})
ypred_nominal = [ 1 if yp > 0.5 else 0 for yp in ypred]
mat = np.matrix(confusion_matrix(y, ypred_nominal))
r1 = round(mat[0,0]/np.sum(mat, axis=1)[0,0]*100, 2)
r2 = round(mat[1,1]/np.sum(mat, axis=1)[1,0]*100, 2)
ov = round((mat[0,0]+mat[1,1])/np.sum(mat)*100, 2)

# ------------------------------------------------------------------------------
print("Loading dataMap...")
f = open("data/"+DBName+"/dataMap.pkl","rb")
dataMap = pickle.load(f)
f.close()

dataMap["figure13"] = "Fig13.png"
dataMap["figure14"] = "Fig14.png"
dataMap["figure15"] = "Fig15.png"
dataMap["figure16"] = "Fig16.png"

dataMap["diagTable"] = "\n".join(tabulate(sample, headers="keys", tablefmt="latex").split("\n")[4:-2])
dataMap["cutOff"] = str(round(cut_off,2))

dataMap["noOfHighLev"] = str(len(high_leverage))
dataMap["indexOfHighLev"] = "They are indexed as %s in the dataset."% (", ".join(high_leverage)) if len(high_leverage)<=5 else ""

dataMap["noOfHighInf"] = str(len(high_influence))
dataMap["indexOfHighInf"] = "They are indexed as %s in the dataset."% (", ".join(high_influence)) if len(high_influence)<=5 else ""

dataMap["tp1"] = str(mat[0,0])
dataMap["fp1"] = str(mat[0,1])
dataMap["t1"] = str(np.sum(mat, axis=1)[0,0])
dataMap["tp2"] = str(mat[1,0])
dataMap["fp2"] = str(mat[1,1])
dataMap["t2"] = str(np.sum(mat, axis=1)[1,0])
dataMap["tt1f2"] = str(np.sum(mat, axis=0)[0,0])
dataMap["tf1t2"] = str(np.sum(mat, axis=0)[0,1])
dataMap["t"] = str(np.sum(mat))

dataMap["accKey1"] = str(round(mat[0,0]/np.sum(mat, axis=1)[0,0]*100, 2))
dataMap["accKey2"] = str(round(mat[1,1]/np.sum(mat, axis=1)[1,0]*100, 2))
dataMap["acc"] = str(round((mat[0,0]+mat[1,1])/np.sum(mat)*100, 2))
dataMap["sureKey1"] = str(round(ov*mat[1,1]/np.sum(mat),2))
dataMap["sureKey2"] = str(round(ov*mat[0,0]/np.sum(mat),2))

dataMap["wellnessKey1"] = "pretty badly " if r1<50 else ""
dataMap["wellnessKey1"] = "fairly " if r1>=50 and r1<70 else ""
dataMap["wellnessKey1"] = "pretty good " if r1>=70 else ""

dataMap["wellnessKey2"] = "also does pretty badly " if r2<50 else ""
dataMap["wellnessKey2"] = "performs fairly well " if r2>=50 and r1<70 else ""
dataMap["wellnessKey2"] = "also performs good " if r2>=70 else ""

print("Writing dataMap...")
f = open("data/"+DBName+"/dataMap.pkl","wb")
pickle.dump(dataMap, f)
f.close()
