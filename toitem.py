# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 22:06:09 2018

@author: ASUS X541U
"""

def itemsets(dataset):
    maxlat= max(seisme[0] for seisme in dataset)
    minlat= min(seisme[0] for seisme in dataset)
    maxlong= max(seisme[1] for seisme in dataset)
    minlong= min(seisme[1] for seisme in dataset)

    moylat = float(maxlat+minlat)/float(2)
    moylong = float(maxlong+minlong)/float(2)
    tableau = []




    for seisme in dataset:
        itemset = []

        h='nul'
        if (seisme[0]<=moylat):
            h='sud '
        else :
            h='nord '
        itemset.append(h)

        q='nul'
        if (seisme[1]<=moylong):
            q='ouest '
        else :
            q='est '
        itemset.append(q)


        p='nul'
        if (seisme[2]<30):
            p='lowdep '
        if ((seisme[2]>=30) and (seisme[2]<100)):
            p='meddep '
        if (seisme[2]>=100):
            p='highdep '
        itemset.append(p)

        m='nul'
        if (seisme[3]<6.0):
            m='lowmag '
        if ((seisme[3]>=6.0) and (seisme[3]<7.0)):
            m='medmag '
        if (seisme[3]>=7.0):
            m='highmag '
        itemset.append(m)

        tableau.append(itemset)


    return (tableau)
"""
if __name__ == "__main__":
    x=[[4.553999999999999, -77.442, 21.3, 7.2], [-30.255, -177.981, 21.4, 6.6]]
    #print itemsets(x)"""
