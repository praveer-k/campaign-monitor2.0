import sys, os, pickle, pylab as pl
import pandas as pd, numpy as np
from datetime import datetime
import helper, graphs as g
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
BASE_DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
# BASE_DATE_FORMAT = "%a %b %d %H:%M:%S %Y"

print("Loading variables ...")
variables  = helper.get_variables("config/variables.yml")
# -----------------------------------------------------------------------------
figpath = "public_html/output/"+DBName
if not os.path.exists(figpath) and not os.path.isdir(figpath):
    print("Creating Plots Folder ...")
    os.mkdir(figpath)
# -----------------------------------------------------------------------------
if not os.path.exists("public_html/output/"+DBName+"/"+DBName+".xlsx"):
    print("No data found...")
    exit()
# -----------------------------------------------------------------------------
print("Loading xlsx output file ...")
xlsx = pd.ExcelFile("public_html/output/"+DBName+"/"+DBName+".xlsx")
df = pd.read_excel(xlsx, "DATA")
# Process data if data non-empty...
if len(df.index)>0:
    # -------- Drop Unwanted Columns -----------------
    df.drop(variables["dropable"], axis=1, inplace=True)
    # ------------ Generate the graphs --------------
    print("Generating graphs...")
    tweet = df["text"].value_counts()
    same_tweets = tweet.apply(lambda x: 1 if x>1 else 0).sum()
    indv_tweets = len(tweet.index)-same_tweets
    legend_labels = ["Same tweets       - "+str(same_tweets),
                     "Independent tweet - "+str(indv_tweets)]
    indexes = [i for i in df.index if df.loc[i,"text"]==tweet.idxmax() ]
    isRT = ["Retweet" if text[:3]=="RT " else "Individual" for text in df["text"]]
    isRT = pd.Series(isRT).value_counts()
    xlabs = ["Individual", "Retweet"]
    xvals = [0 if "Individual" not in isRT.keys() else isRT["Individual"], 0 if "Retweet" not in isRT.keys() else isRT["Retweet"]]
    legend_labels = [ "Retweet - "+str(xvals[1]),
                      "Individual - "+str(xvals[0]) ]

    sub_freq = df["subdivision"].value_counts()
    sub_labs = sub_freq.index.values[:4]
    sub_labs = [l for l in sub_labs if l.lower()!=COUNTRY.lower()]
    sub_vals = pd.Series(sub_freq.values)

    src_freq = df["source"].value_counts()
    src_labs = src_freq.index.values[:3]
    src_labs = [l.lower().replace("twitter","").replace("for","").lstrip().rstrip() for l in src_labs]
    src_vals = pd.Series(src_freq.values)

    scr_name_freq = df["screen_name"].value_counts()
    scr_name_labs = scr_name_freq.index.values[:3]
    scr_name_vals = pd.Series(scr_name_freq.values)
    dataMap = {}

    dataMap["country"] = COUNTRY
    dataMap["keyword1"] = KEYWORD1
    dataMap["keyword2"] = KEYWORD2
    dataMap["dbName"] = DBName
    dataMap["fromDate"] = SINCE
    dataMap["toDate"] = UNTIL

    dataMap["uniqueTweets"] = str(indv_tweets)
    dataMap["sameTweets"] = str(same_tweets)
    dataMap["mostTweeted"] = tweet.idxmax()
    dataMap["tweetIndex"] = str(indexes)[1:-1]
    dataMap["userIndex"] = str(set(df.ix[indexes,"screen_name"]))[1:-1]

    dataMap["individualTweets"] = str(xvals[0])
    dataMap["retweets"] = str(xvals[1])

    dataMap["frequentPlaces"] = ", ".join(sub_labs)
    dataMap["skwenessWRTPlaces"] = "skewed." if sub_vals.max() > sub_vals.quantile(.75)*1.5 else "not skewed."

    dataMap["frequentSources"] = ", ".join(src_labs)[:", ".join(src_labs).rfind(", ")]+" and, "+", ".join(src_labs)[", ".join(src_labs).rfind(", ")+1:]
    dataMap["skewnessWRTSources"] = "skewed." if src_vals.max() > src_vals.quantile(.75)*1.5 else "not skewed."

    dataMap["frequentUsers"] = ", ".join(scr_name_labs)[:", ".join(scr_name_labs).rfind(", ")]+" and, "+", ".join(scr_name_labs)[", ".join(scr_name_labs).rfind(", ")+1:]
    dataMap["skwenessWRTUsers"] = "skewed." if scr_name_vals.max() > scr_name_vals.quantile(.75)*1.5 else "not skewed."

    bar = ChargingBar("Processing", max=12)
    bar.start()
    # -----------------------------------------------------------------------------
    # Analysis of Number of Retweets in the Data...
    # Fig1
    # ------------- Histogram ------------------
    g.Hist(df,colname="text", xlabel="Text", ylabel="Frequency of each tweet", title="Histogram for frequency of tweets", figpath=figpath+"/Fig1.png", legend=legend_labels)
    bar.next()
    # --------------------------------------------
    # Fig2
    # ------------- Bar Plot  ------------------
    pl.figure()
    pl.bar(range(len(xlabs)), xvals, align="center", width=0.1, color=["steelblue", "crimson"])
    pl.xticks(range(len(xlabs)), xlabs)
    pl.xlabel("Retweets and Individual Tweets")
    pl.ylabel("Frequency")
    pl.title("Text Comparision - Individual and Re-Tweets")
    pl.legend(handles=g.patches(legend_labels),prop={"size":10})
    pl.savefig(figpath+"/Fig2.png")
    # pl.show()
    pl.close()
    bar.next()
    # ----------------------------------------
    # Analysis of Location w.r.t to tweets
    # ----- Fig3 Box Plot  ---------------
    g.Boxp(df,colname="subdivision", xlabel="Frequency", ylabel="Places", title="Boxplot of tweets frequency \nfrom various places in "+COUNTRY, figpath=figpath+"/Fig3.png")
    bar.next()
    # ----- Fig4 Horizontal Bar Plot  ----
    g.HBar(df,colname="subdivision", xlabel="Frequency", ylabel="Places", title="Frequency distribution tweets in "+COUNTRY, figpath=figpath+"/Fig4.png")
    bar.next()
    # ----- Fig5 Histogram ---------------
    g.Hist(df,colname="subdivision", xlabel="Places", ylabel="No. of tweets", title="Histogram for tweets Frequency w.r.t places", figpath=figpath+"/Fig5.png")
    bar.next()
    # ----------------------------------------
    # Analysis of Sources w.r.t tweets
    # ----- Fig6 Box plot ----------------
    g.Boxp(df,colname="source", xlabel="Frequency", ylabel="Sources", title="Boxplot of tweets frequency \nfrom various sources", figpath=figpath+"/Fig6.png")
    bar.next()
    # ----- Fig7 Horizontal Bar plot -----
    g.HBar(df,colname="source", xlabel="Frequency", ylabel="Sources", title="Frequency distribution sources of tweets", figpath=figpath+"/Fig7.png")
    bar.next()
    # ----- Fig8 Histogram ---------------
    g.Hist(df,colname="source", xlabel="Sources", ylabel="No. of tweets", title="Histogram for tweets Frequency w.r.t sources", figpath=figpath+"/Fig8.png")
    bar.next()
    # ----------------------------------------
    # Analysis of Users w.r.t to tweets
    # ----- Fig9 Box plot ----------------
    g.Boxp(df,colname="screen_name", xlabel="Frequency", ylabel="Users", title="Boxplot of users frequencies \n of tweets", figpath=figpath+"/Fig9.png")
    bar.next()
    # ----- Fig10 Horizontal Bar plot -----
    g.HBar(df,colname="screen_name", xlabel="Frequency", ylabel="Users", title="Frequency distribution users tweets", figpath=figpath+"/Fig10.png")
    bar.next()
    # ----- Fig11 Histogram ---------------
    g.Hist(df,colname="screen_name", xlabel="users", ylabel="No. of tweets", title="Histogram for users tweeting Frequency", figpath=figpath+"/Fig11.png")
    bar.next()
    # ------------------------------------------------------------------------------
    # -------- Recode the response variable -----------
    df[variables["response"]] = df[variables["response"]].apply(lambda x: 0 if helper.containsAny(KEYWORD1, x) else 1)
    # --------- Fig12 Time Series Graph  ----------
    df.set_index(df["created_at"], inplace=True)
    pl.figure()
    pl.ylim([-1,2])
    locs, labels = pl.yticks([0,1], [KEYWORD1, KEYWORD2])
    pl.setp(labels, size=8)
    df["text"].plot()
    pl.title("Conversation on "+KEYWORD1+" and "+KEYWORD2+" over the period of time")
    pl.xlabel("Tweet Creation Date")
    pl.ylabel("Tweet Talks About ...")
    # pl.show()
    pl.savefig(figpath+"/Fig12.png")
    pl.close()
    bar.next()
    df.reset_index(drop=True, inplace=True)
    bar.finish()
    print("Reducing factor levels for multi_factor columns...")
    # -------- Reducing factor levels for multi_factor columns -------
    for col in variables["multi_factors"]:
        freq = df[col].value_counts()
        newlabel = COUNTRY if col=="subdivision" else "others"
        df[col] = df[col].apply(lambda x: newlabel if x not in freq[:6] else x)
    print("Breaking the time series data into multiple columns...")
    # -------- Break the Time data into multiple columns -------------
    for col in variables["time_series"]:
        df[col] = df[col].apply(lambda x: x.strftime(format="%d-%m-%Y %H:%M:%S"))
        day, mon, yr = df[col].str[:2], df[col].str[3:5], df[col].str[6:10]
        hr, mi, se = df[col].str[11:13],df[col].str[14:16],df[col].str[17:19]
        timeDF = pd.DataFrame({ "day" : day, "mon" : mon, "year": yr,
                                "hrs" : hr , "mins": mi , "secs": se }, columns=["day","mon","year","hrs","mins","secs"])
        timeDF.rename(columns=lambda x : col+"_"+x, inplace=True)
        timeDF = timeDF.astype(int)
        df = pd.concat([df, timeDF], axis=1)
    df.drop(variables["time_series"], axis=1, inplace=True)
    variables["time_series"] = [ col+suffix for col in variables["time_series"] for suffix in ["_day","_mon","_year","_hrs","_mins","_secs"] ]
    # ----------------------------------------
    df["contributors_enabled"] = df["contributors_enabled"].astype(str)
    print("Saving the cleaned dataset ...")
    # ----- Drop columns which have only one factor --------
    for column in df:
        if len(df[column].unique()) <= 1:
            df.drop(column, axis=1, inplace=True)
    # -------------- Drop duplicate columns -----------------
    remove = []
    cols = df.columns
    for i in range(len(cols)-1):
        v = df[cols[i]].values
        for j in range(i+1,len(cols)):
            if np.array_equal(v,df[cols[j]].values):
                remove.append(cols[j])
    df.drop(remove, axis=1, inplace=True)
    # ------- Drop `na` and duplicate rows ---------
    df.dropna(axis=1, how="all", inplace=True)
    df.drop_duplicates(inplace=True)
    # -----------------------------------------------------------------------------
    # -----------------------------------------------------------------------------
    # ------------------ DATA MAP FOR THE REPORT ----------------------------------
    # -----------------------------------------------------------------------------
    dataMap["figure1"] = "Fig1.png"
    dataMap["figure2"] = "Fig2.png"
    dataMap["figure3"] = "Fig3.png"
    dataMap["figure4"] = "Fig4.png"
    dataMap["figure5"] = "Fig5.png"
    dataMap["figure6"] = "Fig6.png"
    dataMap["figure7"] = "Fig7.png"
    dataMap["figure8"] = "Fig8.png"
    dataMap["figure9"] = "Fig9.png"
    dataMap["figure10"] = "Fig10.png"
    dataMap["figure11"] = "Fig11.png"
    dataMap["figure12"] = "Fig12.png"

    f = open("data/"+DBName+"/dataMap.pkl","wb")
    pickle.dump(dataMap, f)
    f.close()
df.to_excel(figpath+"/"+DBName+"_clean.xlsx", sheet_name="DATA", index=False)
print("Done.")
