import matplotlib.patches as mpatches
import pylab as pl
import pandas as pd

def patches(legend_labels):
    patches = []
    for l in legend_labels:
        patches.append( mpatches.Patch(color="limegreen", label=l) )
    return patches

def summary_legend(vals):
    dis = pd.Series(vals)
    llabels = [ "Count  - " + str(dis.count())        ,
                "Std    - " + str(round(dis.std(),2)) ,
                "Min    - " + str(dis.min())          ,
                "Max    - " + str(dis.max())          ,
                "Mean   - " + str(round(dis.mean(),2)),
                "Q1     - " + str(dis.quantile(.25))  ,
                "Median - " + str(dis.median())       ,
                "Q3     - " + str(dis.quantile(.75))  ,
                "Mode   - " + str(dis.mode())     ]
    return patches(llabels)

def Hist(df, colname, xlabel, ylabel, title, figpath, legend=None):
    keys = list(df[colname].values)
    freq = [keys.index(k) for k in keys]
    pl.figure()
    pl.grid(True)
    pl.hist(freq, len(keys), histtype="bar")
    pl.xlabel(xlabel)
    pl.ylabel(ylabel)
    pl.title(title)
    if legend!=None:
        pl.legend(handles=patches(legend), prop={"size":10})
    pl.savefig(figpath)
    # pl.show()
    pl.close()

def HBar(df, colname, xlabel, ylabel, title, figpath):
    freq = df[colname].value_counts()
    ylabs = freq.index.values[:30]
    yvals = freq.values[:30]
    pl.figure()
    pl.grid(True)
    pos = pl.arange(30)+0.5 if len(ylabs)>30 else pl.arange(len(ylabs))+0.5
    locs, labels = pl.yticks(pos, ylabs)
    pl.setp(labels, size=8)
    pl.barh(pos, yvals, align="center", color=["crimson", "steelblue"])
    pl.xlabel(xlabel)
    pl.ylabel(ylabel)
    pl.title(title)
    pl.legend(handles=summary_legend(yvals),prop={"size":10})
    pl.tight_layout()
    pl.savefig(figpath)
    # pl.show()
    pl.close()

def Boxp(df, colname, xlabel, ylabel, title, figpath):
    freq = df[colname].value_counts() # sorted frequencies
    pl.figure()
    pl.grid(True)
    pl.boxplot(freq.values)
    pl.xlabel(xlabel)
    pl.ylabel(ylabel)
    pl.title(title)
    pl.legend(handles=summary_legend(freq.values),prop={"size":10})
    pl.tight_layout()
    pl.savefig(figpath)
    # pl.show()
    pl.close()
