# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 19:38:03 2018

@author: ASUS X541U
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import pandas as pd
import plotly.graph_objs as go
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples, silhouette_score

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import reglesgen
from toitem import *

#==============================================================================
#           Retourne une liste de seismes 
#==============================================================================
def preprocessone(data):
    
    df=pd.read_csv(data)
    #list_drop = ['locationSource','status','type','time','id','magType', 'nst', 'magNst', 'magError', 'horizontalError', 'depthError','net','place','updated','magSource']
    df1=df.iloc[:,[0,1,2,3,4,11]]
    df1=df1.dropna(axis=0, how='any')
    df1.columns=['Date','lat','long','depth','mag','id']
    dd=df1.values.tolist()
    data=np.array(dd)
    kmeans = KMeans(n_clusters=k,init='k-means++', max_iter=1000).fit(data)


    
def preprocesstwo(tab):
    pre=tab.tolist()
    pre=itemsets(tab)
    tab=np.array(pre)
    return tab 

def numbermag(df,low,med,high):
    statm=[]
    df1=df.loc[(df['mag'] >= low) & df['mag'] <= med]
    statm.append(df1.shape[0])
    df1=df.loc[(df['mag'] > med)& df['mag'] <= high]
    statm.append(df1.shape[0])
    df1=df.loc[df['mag'] > high]
    statm.append(df1.shape[0])
    return statm

def numberdepth(df,low,med,high):
    statd=[]
    df1=df.loc[(df['mag'] >= low) & df['mag'] <= med]
    statd.append(df1.shape[0])
    df1=df.loc[(df['mag'] > med)& df['mag'] <= high]
    statd.append(df1.shape[0])
    df1=df.loc[df['mag'] > high]
    statd.append(df1.shape[0])
    return statd

def histo(df,crit) :
    statd=[]
    df1=df[crit]
    stat=np.array(df1)
    return stat
   
"""if __name__ == '__main__':
    df=pd.read_csv("C:\Users\ASUS X541U\Downloads\query.csv")
    df1=df.iloc[:,[1,2,3,4]]
    df1=df1.dropna(axis=0, how='any')
    k=3
    df1.columns=['lat','long','depth','mag']
    listclst=[]
    [ listclst.append("Cluster"+str(i)) for i in range(1,k+1) ]
    print listclst"""

    