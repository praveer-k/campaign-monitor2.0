import sys, os, pickle, json
import pandas as pd, numpy as np
import patsy, statsmodels.api as sm
import helper
from tabulate import tabulate
import collections

path = sys.argv[1]
with open(path) as f:
    keys = f.readlines()
    KEYWORD1 = keys[0].rstrip()
    KEYWORD2 = keys[1].rstrip()
    SINCE    = keys[2].rstrip()
    UNTIL    = keys[3].rstrip()
    DBName   = keys[4].rstrip()
    COUNTRY  = keys[5].rstrip()

filepath = "public_html/output/"+DBName
# -----------------------------------------------------------------------------
if not os.path.exists("public_html/output/"+DBName+"/"+DBName+"_clean.xlsx"):
    print("No data found...")
    exit()
# -----------------------------------------------------------------------------
print("Loading cleaned xlsx output file ...")
xlsx = pd.ExcelFile("public_html/output/"+DBName+"/"+DBName+"_clean.xlsx")
df = pd.read_excel(xlsx, "DATA")
# Process data if data non-empty...
if len(df.index)>0:
    formulas = [ "text ~ source + subdivision + statuses_count + followers_count + retweet_count + contributors_enabled + category + confidence + created_at_day + created_at_mon + created_at_year",
                 "text ~ source + subdivision + statuses_count + followers_count + retweet_count + contributors_enabled + category + confidence + category:confidence + created_at_day + created_at_mon + created_at_year + created_at_day:created_at_mon:created_at_year",
                 "text ~ source + subdivision + statuses_count + followers_count + retweet_count + contributors_enabled + category + category:confidence + created_at_day:created_at_mon:created_at_year",
                 "text ~ source + subdivision + statuses_count + followers_count + retweet_count + contributors_enabled + category:confidence + created_at_day:created_at_mon:created_at_year"
               ]
    results = []
    print("Model Selection...")
    for formula in formulas:
        formula = helper.removeUnwanted(formula, df.columns)
        y,X = patsy.dmatrices(formula, df, return_type="dataframe")
        logit = sm.Logit(y, X)
        result = logit.fit(method="bfgs")
        results.append( (formula, y, X, result) )

    table = {"Model":[],"AIC":[]}
    i = 1
    for result in results:
        table["Model"].append("Model "+str(i))
        table["AIC"].append(result[3].aic)
        i += 1

    # results = [result for result in results if result[3].mle_retvals["converged"]==True]
    formula, y, X, result = min(results, key=lambda x: x[3].aic)

    print("Best Model : ", formula)
    print("saving the model...")
    model = { "formula": formula, "y": y, "X": X, "result": result }
    f = open("data/"+DBName+"/model.pkl", "wb")
    pickle.dump(model, f)
    f.close()
    # -----------------------------------------------------------------------------
    conf = result.conf_int()
    conf["OR"] = result.params
    conf.columns = ["Lower CI", "Upper CI", "_Odds Ratio"]
    conf = np.exp(conf)
    indexes = conf.index
    conf.reset_index(drop=True, inplace=True)
    conf = conf.to_dict(orient="list")
    conf["Discriptors"] = indexes
    conf = collections.OrderedDict(sorted(conf.items()))

    sig = [k for k, v in result.pvalues.iteritems() if v<=0.05 ]
    insig = [k for k, v in result.pvalues.iteritems() if v>0.05 ]

    listOfComments = []
    refdict = helper.getRefDict(X.columns, df)
    print("Loading variables ...")
    variables  = helper.get_variables("config/variables.yml")
    for k, v in result.params.iteritems():
        if k in sig:
            key = k[:k.find("[")] if k.find("[")!=-1 else k
            val = round(np.exp(v)*100,2)
            if key.lower()=="intercept":
                text  = "The odds of people voting for %s is " % (KEYWORD2)
                text += "%s more likely to occur" % (str(val-100)+"%") if val>100 else ""
                text += "%s less likely to occur" % (str(val-100)+"%") if val<100 else ""
                text += "equally likely to occur w.r.t %s" % (KEYWORD1) if val==100 else ""
                text += ", if there is no one voting/tweeting."
            elif key in variables["numeric"] and k.find(":")==-1 and k.find("*")==-1:
                text  = "For 1 unit increase in %s the odds of people voting for %s is likely to "% (key, KEYWORD2)
                text += "increase" if val>100 else ""
                text += "decrease" if val<100 else ""
                text += "by %s" % (str(abs(val-100))+"%")
                text  = "The odds of people voting for %s does not change w.r.t %s." % (KEYWORD2, key) if val==100 else ""
            elif key in refdict.keys() and k.find(":")==-1 and k.find("*")==-1:
                lookfor = "[T." if k.find("[T.")!=-1 else "["
                myvar = k[k.find(lookfor)+len(lookfor):-1]
                text  = "The odds of people voting for %s is "%(KEYWORD2)
                text += "more" if val>100 else ""
                text += "less" if val<100 else ""
                text += "equally" if val==100 else ""
                text += "likely when the %s is %s as compared to %s "%(key, myvar, refdict[key])
                text += "by %s." % (str(abs(val-100))+"%") if val!=100 else "."
            else: #Interaction terms
                text = ""
            if text!="":
                listOfComments.append("\item "+text)
    # -----------------------------------------------------------------------------
    print("Loading dataMap...")
    f = open("data/"+DBName+"/dataMap.pkl","rb")
    dataMap = pickle.load(f)
    f.close()

    dataMap["modelAIC"] = "\n".join(tabulate(table, headers="keys", tablefmt="latex").split("\n")[4:-2])
    dataMap["bestModelFormula"] = formula
    dataMap["modelSummary"] = helper.addtabs(str(result.summary()), 2)
    dataMap["llrPValue"] = str(result.llr_pvalue)
    dataMap["moreOrLess"] = "more" if result.llr_pvalue>0.05 else "less"
    dataMap["rejectedOrAccepted"] =  "accepted" if result.llr_pvalue>0.05 else "rejected"
    dataMap["dependentOrIndependent"] = "independent" if result.llr_pvalue>0.05 else "dependent"
    dataMap["extraComment"] = "So, we do not proceed with further diagnostics." if result.llr_pvalue>0.05 else "less"
    dataMap["OddsandCI"] = "\n".join(tabulate(conf, headers="keys", tablefmt="latex").split("\n")[4:-2])

    dataMap["sigVars"] = helper.prettyjoin(sig, df.columns)
    dataMap["inSigVars"] = helper.prettyjoin(insig, df.columns)

    dataMap["listOfComments"] = "\n".join(listOfComments)
    print("Writing dataMap...")
    f = open("data/"+DBName+"/dataMap.pkl","wb")
    pickle.dump(dataMap, f)
    f.close()
print("Done.")
