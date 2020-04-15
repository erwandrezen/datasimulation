# generation automatique de fichiers

import pandas as pd
import json
import datetime

import random
#import numpy.random as rd


f_errors = json.load(open("param_errors.json"))
l_scenarios=f_errors['scenarios']
l_param=f_errors['parameters']
pct_err=l_param["pct_err"]
init_file=l_param["init_file"]

df_file=pd.read_csv(init_file, sep=';')


df_init=df_file[(df_file['mark']==l_param['init'])]
                            
l_init=df_init.index.values.tolist()
# nb erreurs calcule selon le nb d'evt
nb_err=int(pct_err*len(df_file))


# fixer la série "aleatoire" ?
#random.seed(?)


for s, scen in enumerate(l_scenarios):
    
    nb_files=l_scenarios[s]["nb_files"]
    l_events=l_scenarios[s]["evt"]
    for f in range(nb_files):
        file_name=l_scenarios[s]["scenario"]+"_n"+str(f)+".csv"
        df_err=df_file.copy()
        err=0
        for e,evt in enumerate(l_scenarios[s]["evt"]):
            l_evt=random.sample(range(0,len(df_file)),nb_err)
            #l_init_sel=random.sample(range(0,len(l_init)),nb_err)
            l_init_sel=random.sample(l_init,nb_err)
            err=err+int(nb_err*evt['pct_err'])
            for p in range(err):
                if evt['err']=='yob':
                    if evt['typ_err']=='null':
                        df_err['yob'][l_evt[p]]=None
                    if evt['typ_err']=='':
                        df_err['yob'][l_evt[p]]=2030
                        
                if evt['err']=='mob':
                    if evt['typ_err']=='null':
                        df_err['mob'][l_evt[p]]=None
                    if evt['typ_err']=='':
                        df_err['mob'][l_evt[p]]='99'    
                        
                if evt['err']=='death':
                    if evt['typ_err']=='null':
                        df_err['death_dte'][l_evt[p]]=None
                        df_err['death_ts'][l_evt[p]]=None
                    if evt['typ_err']=='date':   
                        if pd.isnull(df_err['death_dte'][l_evt[p]]):
                            df_err['death_dte'][l_evt[p]]=pd.to_datetime('2030-01-01', format="%Y-%m-%d")
                            df_err['death_ts'][l_evt[p]]=47483
                        else:
                            df_err['death_dte'][l_evt[p]]=pd.to_datetime(df_err['death_dte'][l_evt[p]])+datetime.timedelta(days=evt['err_sd'])
                            df_err['death_ts'][l_evt[p]]=(pd.to_datetime(df_err['death_dte'][l_evt[p]])+datetime.timedelta(days=evt['err_sd'])-pd.to_datetime('1900-01-01')).days
                            
                if evt['err']=='mark':
                    if evt['typ_err']=='null':
                        df_err['mark_dte'][l_evt[p]]=None  
                        df_err['mark_ts'][l_evt[p]]=None  
                    if evt['typ_err']=='date':   
                        df_err['mark_dte'][l_evt[p]]=pd.to_datetime(df_err['mark_dte'][l_evt[p]])+datetime.timedelta(days=evt['err_sd'])
                        df_err['mark_ts'][l_evt[p]]=(pd.to_datetime(df_err['mark_dte'][l_evt[p]])+datetime.timedelta(days=evt['err_sd'])-pd.to_datetime('1900-01-01')).days
                    if evt['typ_err']=='add': 
                        df_add=df_init.copy()
                        df_add['mark_dte']=pd.to_datetime(df_add['mark_dte'])+datetime.timedelta(days=evt['err_sd'])
                        df_add['mark_ts']=df_add['mark_ts']+evt['err_sd']
                        df_err=pd.DataFrame(df_add[df_add.index==[l_init_sel[p]]]).append(df_err, ignore_index=True) 
                    if evt['typ_err']=='del': 
                        df_err=df_err.drop([l_init_sel[p]])

                        

        df_err.to_csv(l_param["rep_err"]+file_name,index=False,sep=';')                

       