# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 19:53:17 2018

@author: ASUS X541U
"""

#from preproc import *
import pandas as pd
import toitem
from sklearn.cluster import KMeans
import numpy as np
from convert import *
from fp_growth import *
from association import *
from toitem import *
from sklearn.preprocessing import scale
from sklearn.preprocessing import StandardScaler

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

def nbreyear(df1):
    df1['Date']=pd.to_datetime(df1['Date'])
    df2 = df1.set_index(['Date'])
    year_nbr=df2.groupby(df2.index.year).size().reset_index(name='Number_Earthquakes')
    return year_nbr

def ClusterIndicesNumpy(clustNum, labels_array): #numpy
    return np.where(labels_array == clustNum)[0]



def itemsf(transactions,minsup):
    result = []
    for itemset, support in find_frequent_itemsets(transactions, minsup, True):
        support=supportconvert2(support, len(transactions))
        result.append([support,itemset])
        result = sorted(result, key=lambda i: i[0])
    #print result
    return result
    """for itemset, support in result:
        print str(itemset) + ' ' + str(support)"""


def getrules(res):
    col=['support','itemsets']
    df=pd.DataFrame(res,columns=col)
    #print df
    rules=association_rules(df,min_threshold=0.2)
    """rules["antecedant_len"] = rules["antecedants"].apply(lambda x: len(x))"""
    #rules=rules[ (rules['confidence'] >= 0.8) ]
    return rules

def genererregles(kmeans,k,data):

        regles=[]
        for i in range(0,k) :
            print "Cluster",i+1
            c=data[ClusterIndicesNumpy(i,kmeans.labels_)] # np array du cluster i
            d = preprocesstwo(c) # normalise le cluster
            m=itemsf(d,5)
            if len(m)==0 :
                print "No frequent itemset for cluster",i+1
            else :
                df5=getrules(m)
                liste = list(df5['antecedants'])
                listant=([list(x) for x in liste])
                liste = list(df5['consequents'])
                listcons = ([list(x) for x in liste])
                n = df5.columns[0]
                df5.drop(n, axis = 1, inplace = True)
                df5[n] = listant
                n = df5.columns[0]
                df5.drop(n, axis = 1, inplace = True)
                df5[n] = listcons
                df5=df5.drop(['leverage', 'conviction','consequent support','antecedent support','lift'], axis=1)
                regles.append(df5)

        return regles

def idto(ids,df) :
    center = pd.DataFrame()
    for i in ids :
        center=center.append(df.loc[df['id'] == i])
    print center
    center=center.iloc[:,[1,2,3,4]]
    center=center.values
    print center
    return center

if __name__ == "__main__":
    #df=pd.read_csv("C:\Users\ASUS X541U\Downloads\query.csv")
    #df1=df.iloc[:,[0,1,2,3,4,11]]
    #df=pd.read_csv("C:\Users\ASUS X541U\Desktop\Catalogues\isc-gem-cat.csv")
    #df1=df.iloc[:,[0,1,2,7,10,23]]
    df=pd.read_csv('C:/Users/ASUS X541U/Desktop/Catalogues/database.csv')
    df=df[(df['Type']=='Earthquake') & (df['Depth']> 0)]
    df1=df.iloc[:,[0,1,2,3,5,8]]
    df1=df1.dropna(axis=0, how='any')
    #df1.columns=['Date','Heure','lat','long','depth','mag']
    df1.columns=['Date','lat','long','depth','mag','id']
    print df1

    #print df1
    """
    df_table=df1
    dd=df1.values.tolist()
    data=np.array(dd)
    ids=['usp000exfn','usp000jr55']
    #center=df1.loc[df1['id'] == ids[0]]
    idto(ids)

    data=np.array(dd)
    data=scale(df1[['lat','long','depth','mag']])
    abc=scalery.inverse_transform(data)
    print data
    df1=df1.iloc[:,[1,2,3,4]]
    #df1=df1.iloc[:,[2,3,4,5]]
    #print df1
    dd=df1.values.tolist()
    colonnes=['lat','long','depth','mag']
    datax=np.array(dd)
    k=3
    kmeans = KMeans(n_clusters=3,init='k-means++', max_iter=1000).fit(datax)
    regle=genererregles(kmeans,k,datax)
    #print regle
    """
