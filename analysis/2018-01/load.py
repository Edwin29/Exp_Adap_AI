import pandas as pd, numpy as np, glob, sys
cols="d t w b we be wd bd tc r te ev eco wt bt clk evl n".split()
def load(files):
    dfs=[pd.read_csv(f,sep="\t",names=cols,header=None,quoting=3,dtype=str,na_filter=False,compression="gzip") for f in files]
    return pd.concat(dfs,ignore_index=True)
