# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 11:26:34 2020

@author: s20kerbr
"""

# generation automatique de fichiers

import pandas as pd



header_row = ['nivgeo','codgeo','libgeo','sexe','AGED100' ,'nb']
header_x = ['codgeo','sexe','AGED100' ,'nb']

header_com=['codgeo','dep','reg','ptot','weight_fr','weight_reg','weight_dep']
header_com2=['codgeo','dep','reg','ptot']

dtype_com={'codgeo': str}

pop1=pd.read_csv(filepath_or_buffer='F:/work/Nomenclatures/GEO/BTT_TD_POP1B_2016/BTT_TD_POP1B_2016.csv',sep=';', dtype=dtype_com, header=0, names=header_row,usecols=header_x)
com=pd.read_csv(filepath_or_buffer='F:/work/Données simulées/data_ref/communes_fr.csv',sep=';', dtype=dtype_com, header=0, names=header_com,usecols=header_com2)
dep=pd.read_csv(filepath_or_buffer='F:/work/Données simulées/data_ref/dep.csv',sep=';')
ref=pd.read_csv(filepath_or_buffer='F:/work/Données simulées/data_ref/reg.csv',sep=';')




pop1['nb']=pop1['nb'].astype(float)
pop1['nb_int']=pop1['nb'].astype(int)
pop1['age']=pop1['AGED100'].astype(int)


pop=pd.merge(pop1,com,on='codgeo',how='left')



# preparation fichier pop men
# ###########################################################################
df_men_age1=pop.loc[(pop['sexe']==1), ['codgeo','age' ,'nb_int','dep','reg'] ]

# aggreation par commune (hors age)
df_men1=df_men_age1.groupby(['codgeo','dep','reg'], as_index=False)["nb_int"].sum()
# aggreation par age dep reg 
df_age_m1=df_men_age1.groupby(['age','dep','reg'], as_index=False)["nb_int"].sum()
# aggreation par age reg 
df_age_m_reg=df_men_age1.groupby(['age','reg'], as_index=False)["nb_int"].sum()
# aggreation par hors age
df_age_m_fr=df_men_age1.groupby(['age'], as_index=False)["nb_int"].sum()


# totaux geographique (dep, reg, fr) de la pop men
dep_men=df_men_age1.groupby("dep", as_index=False)["nb_int"].sum()
dep_men = dep_men.rename(columns = {'nb_int':'pop_dep'})

reg_men=df_men_age1.groupby("reg", as_index=False)["nb_int"].sum()
reg_men = reg_men.rename(columns = {'nb_int':'pop_reg'})

# calcul de la proportion de la pop men par dep, reg ou fr
df_men2=pd.merge(df_men1,dep_men,on='dep',how='left')
df_men=pd.merge(df_men2,reg_men,on='reg',how='left')

df_men['weight_dep']=(df_men['nb_int']/df_men['pop_dep']*100000)
df_men['weight_dep']=df_men['weight_dep'].fillna(0.0).astype(int)


df_men['weight_reg']=(df_men['nb_int']/df_men['pop_reg']*100000)
df_men['weight_reg']=df_men['weight_reg'].fillna(0.0).astype(int)

nb_men=df_men_age1["nb_int"].sum()
df_men['weight_fr']=df_men['nb_int']/nb_men*1000000
df_men['weight_fr']=df_men['weight_fr'].fillna(0.0).astype(int)

df_men.to_csv('F:/work/Données simulées/data_ref/geo_men.csv',index=False,columns= ['codgeo','dep','reg','weight_dep','weight_reg','weight_fr'])



# calcul de la proportion de la pop men par age dep, reg 
df_age_m2=pd.merge(df_age_m1,dep_men,on='dep',how='left')
df_age_m=pd.merge(df_age_m2,reg_men,on='reg',how='left')

df_age_m['weight_dep']=(df_age_m['nb_int']/df_men['pop_dep']*1000)+1
df_age_m['weight_dep']=df_age_m['weight_dep'].fillna(0.0).astype(int)


df_age_m['weight_reg']=(df_age_m['nb_int']/df_men['pop_reg']*10000)+1
df_age_m['weight_reg']=df_age_m['weight_reg'].fillna(0.0).astype(int)

df_age_m_reg['weight_reg']=(df_age_m_reg['nb_int']/df_men['pop_reg']*10000)+1
df_age_m_reg['weight_reg']=df_age_m_reg['weight_reg'].fillna(0.0).astype(int)

# calcul de la proportion de la pop men par age fr
df_age_m_fr['weight_fr']=df_age_m_fr['nb_int']/nb_men*1000+1
df_age_m_fr['weight_fr']=df_age_m_fr['weight_fr'].fillna(0.0).astype(int)

df_age_m.to_csv('F:/work/Données simulées/data_ref/age_men.csv',index=False,columns= ['age','dep','reg','weight_dep','weight_reg'])
df_age_m_reg.to_csv('F:/work/Données simulées/data_ref/age_men_reg.csv',index=False,columns= ['age','reg','weight_reg'])

df_age_m_fr.to_csv('F:/work/Données simulées/data_ref/age_men_fr.csv',index=False,columns= ['age','weight_fr'])


# calcul de la proportion de la pop men par age et par dep, reg ou fr
df_men_age2=pd.merge(df_men_age1,dep_men,on='dep',how='left')
df_men_age=pd.merge(df_men_age2,reg_men,on='reg',how='left')

df_men_age['weight_dep']=(df_men_age['nb_int']/df_men_age['pop_dep']*100000)
df_men_age['weight_dep']=df_men_age['weight_dep'].fillna(0.0).astype(int)


df_men_age['weight_reg']=(df_men_age['nb_int']/df_men_age['pop_reg']*100000)
df_men_age['weight_reg']=df_men_age['weight_reg'].fillna(0.0).astype(int)

nb_men=df_men_age["nb_int"].sum()
df_men_age['weight_fr']=df_men_age['nb_int']/nb_men*1000000
df_men_age['weight_fr']=df_men_age['weight_fr'].fillna(0.0).astype(int)

df_men_age.to_csv('F:/work/Données simulées/data_ref/geo_men_age.csv',index=False,columns= ['codgeo','age','dep','reg','weight_dep','weight_reg','weight_fr'])



# preparation fichier pop women
# ###########################################################################
df_women_age1=pop.loc[(pop['sexe']==2), ['codgeo','age' ,'nb_int','dep','reg'] ]

# aggreation par commune (hors age)
df_women1=df_women_age1.groupby(['codgeo','dep','reg'], as_index=False)["nb_int"].sum()
# aggreation par age dep reg 
df_age_w1=df_women_age1.groupby(['age','dep','reg'], as_index=False)["nb_int"].sum()
# aggreation par age reg 
df_age_w_reg=df_women_age1.groupby(['age','reg'], as_index=False)["nb_int"].sum()
# aggreation par hors age
df_age_w_fr=df_women_age1.groupby(['age'], as_index=False)["nb_int"].sum()


# totaux geographique (dep, reg, fr) de la pop women
dep_women=df_women_age1.groupby("dep", as_index=False)["nb_int"].sum()
dep_women = dep_women.rename(columns = {'nb_int':'pop_dep'})

reg_women=df_women_age1.groupby("reg", as_index=False)["nb_int"].sum()
reg_women = reg_women.rename(columns = {'nb_int':'pop_reg'})

# calcul de la proportion de la pop women par dep, reg ou fr
df_women2=pd.merge(df_women1,dep_women,on='dep',how='left')
df_women=pd.merge(df_women2,reg_women,on='reg',how='left')

df_women['weight_dep']=(df_women['nb_int']/df_women['pop_dep']*100000)
df_women['weight_dep']=df_women['weight_dep'].fillna(0.0).astype(int)


df_women['weight_reg']=(df_women['nb_int']/df_women['pop_reg']*100000)
df_women['weight_reg']=df_women['weight_reg'].fillna(0.0).astype(int)

nb_women=df_women_age1["nb_int"].sum()
df_women['weight_fr']=df_women['nb_int']/nb_women*1000000
df_women['weight_fr']=df_women['weight_fr'].fillna(0.0).astype(int)

df_women.to_csv('F:/work/Données simulées/data_ref/geo_women.csv',index=False,columns= ['codgeo','dep','reg','weight_dep','weight_reg','weight_fr'])



# calcul de la proportion de la pop women par age dep, reg 
df_age_w2=pd.merge(df_age_w1,dep_women,on='dep',how='left')
df_age_w=pd.merge(df_age_w2,reg_women,on='reg',how='left')

df_age_w['weight_dep']=(df_age_w['nb_int']/df_women['pop_dep']*1000)+1
df_age_w['weight_dep']=df_age_w['weight_dep'].fillna(0.0).astype(int)


df_age_w['weight_reg']=(df_age_w['nb_int']/df_women['pop_reg']*10000)+1
df_age_w['weight_reg']=df_age_w['weight_reg'].fillna(0.0).astype(int)

df_age_w_reg['weight_reg']=(df_age_w['nb_int']/df_women['pop_reg']*10000)+1
df_age_w_reg['weight_reg']=df_age_w['weight_reg'].fillna(0.0).astype(int)


# calcul de la proportion de la pop women par age fr
df_age_w_fr['weight_fr']=df_age_w_fr['nb_int']/nb_women*1000+1
df_age_w_fr['weight_fr']=df_age_w_fr['weight_fr'].fillna(0.0).astype(int)

df_age_w.to_csv('F:/work/Données simulées/data_ref/age_women.csv',index=False,columns= ['age','dep','reg','weight_dep','weight_reg'])
df_age_w_reg.to_csv('F:/work/Données simulées/data_ref/age_women_reg.csv',index=False,columns= ['age','reg','weight_reg'])
df_age_w_fr.to_csv('F:/work/Données simulées/data_ref/age_women_fr.csv',index=False,columns= ['age','weight_fr'])


# calcul de la proportion de la pop women par age et par dep, reg ou fr
df_women_age2=pd.merge(df_women_age1,dep_women,on='dep',how='left')
df_women_age=pd.merge(df_women_age2,reg_women,on='reg',how='left')

df_women_age['weight_dep']=(df_women_age['nb_int']/df_women_age['pop_dep']*100000)
df_women_age['weight_dep']=df_women_age['weight_dep'].fillna(0.0).astype(int)


df_women_age['weight_reg']=(df_women_age['nb_int']/df_women_age['pop_reg']*100000)
df_women_age['weight_reg']=df_women_age['weight_reg'].fillna(0.0).astype(int)

nb_women=df_women_age["nb_int"].sum()
df_women_age['weight_fr']=df_women_age['nb_int']/nb_women*1000000
df_women_age['weight_fr']=df_women_age['weight_fr'].fillna(0.0).astype(int)

df_women_age.to_csv('F:/work/Données simulées/data_ref/geo_women_age.csv',index=False,columns= ['codgeo','age','dep','reg','weight_dep','weight_reg','weight_fr'])
