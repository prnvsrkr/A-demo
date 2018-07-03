# -*- coding: utf-8 -*-
"""
Created on Tue May 22 08:44:42 2018

@author: Pranav
"""
import pandas as pd
import numpy as np
import operator

op={'<':operator.lt,'>':operator.gt,'==':operator.eq}


Rules=pd.read_csv('C:/Users/Pranav/Desktop/project/Ready_Files/CMMH/Rules.csv',sep='\t')
Rules.reset_index(drop=True,inplace=True)
Rules.Value=pd.to_numeric(Rules.Value,errors='ignore')




MH01=pd.read_csv('C:/Users/Pranav/Desktop/project/Ready_Files/CMMH/MH01.csv',sep='\t')
MH02=pd.read_csv('C:/Users/Pranav/Desktop/project/Ready_Files/CMMH/MH02.csv',sep='\t')
MH03=pd.read_csv('C:/Users/Pranav/Desktop/project/Ready_Files/CMMH/MH03.csv',sep='\t')

for i in range(len(Rules)):
    globals()[Rules.Machine[i]]['rule{}'.format(i)]=True
    globals()[Rules.Machine[i]]['TIME STAMP']= pd.to_datetime(globals()[Rules.Machine[i]]['TIME STAMP'], infer_datetime_format=True)




for i in range(len(Rules)):
    operator=op[Rules.Operator[i]]
    if(len(Rules.Value[i])<10):
        a=operator(globals()[Rules.Machine[i]][globals()[Rules.Machine[i]].columns[globals()[Rules.Machine[i]].columns==Rules.Attribute[i]].values],int(Rules.Value[i]))
    else:
        expr=int(eval(Rules.Value[i]))
        a=operator(globals()[Rules.Machine[i]][globals()[Rules.Machine[i]].columns[globals()[Rules.Machine[i]].columns==Rules.Attribute[i]].values],expr)
    a=np.array(a)    
    for j in range(len(a)):
        if(a[j]==False):
            globals()[Rules.Machine[i]]['rule{}'.format(i)]=a
            
            
rule_broken=list()

MH01_rules=list(MH01.columns[MH01.columns.str.contains('rule')].values)
MH02_rules=list(MH02.columns[MH02.columns.str.contains('rule')].values)
MH03_rules=list(MH03.columns[MH03.columns.str.contains('rule')].values)


def breakdetect(rule_broken):
    for i in range(len(MH01_rules)):
       if(any(MH01[MH01_rules[i]]==False)):
           rule_broken.append(MH01_rules[i])
    for i in range(len(MH02_rules)):
       if(any(MH02[MH02_rules[i]]==False)):
           rule_broken.append(MH02_rules[i])
    for i in range(len(MH03_rules)):
       if(any(MH03[MH03_rules[i]]==False)):
           rule_broken.append(MH03_rules[i])
    return rule_broken 


def prov_index(rule_broken):
    rule_broken_index=list()
    for i in range(len(rule_broken)):
        rule_broken_index.append(rule_broken[i].split('e')[1])
    return rule_broken_index
    




rule_broken=breakdetect(rule_broken)
rule_broken_index=pd.to_numeric(prov_index(rule_broken))   

 
        
        
    
    
    