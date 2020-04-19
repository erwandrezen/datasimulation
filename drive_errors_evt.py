# generation automatique de fichiers

import pandas as pd
import json
import datetime
import sys
import random


################################################################################
def gen_com():
    # attribution aleatoire ponderee (cf. recensement (weight)) de la commune de residence
    # selon le niveau geo
    com = random.choices(l_depcom,l_comweight)[0]
    
    return com



if len(sys.argv)<1:
    print ("You must provide :")
    print ("   1) [IN]  a json parameter file")
    sys.exit()

if len(sys.argv)==0:
    file_param   = sys.argv[1]
else:
    file_param='param_errors.json'


f_errors = json.load(open(file_param))
l_scenarios=f_errors['scenarios']
l_param=f_errors['parameters']
pct_err=l_param["pct_err"]
init_file=l_param["init_file"]


# constitution du dataframe geo correspondant aux paramètres choisis
# tirage au sort de la commune au niveau de la Fr, d'une région ou d'un departement
if l_param['geo_level']=='fr':
    header_row = ['DEPCOM', 'DEP', 'REG', 'PTOT', 'weight', 'weight_reg', 'weight_dep']
    df=pd.read_csv(filepath_or_buffer='data_ref/communes_fr.csv',sep=';', header=0, names=header_row)
    df_com=df

elif l_param['geo_level']=='reg':
    header_row = ['DEPCOM', 'DEP', 'REG', 'PTOT', 'weight_fr', 'weight', 'weight_dep']
    df=pd.read_csv(filepath_or_buffer='data_ref/communes_fr.csv',sep=';',header=0, names=header_row)
    df_com=df[(df['REG']==l_param['geo_sel'])]

elif l_param['geo_level']=='dep':
    header_row = ['DEPCOM', 'DEP', 'REG', 'PTOT', 'weight_fr', 'weight_reg', 'weight']
    df=pd.read_csv(filepath_or_buffer='data_ref/communes_fr.csv',sep=';', header=0, names=header_row)
    df_com=df[(df['DEP']==l_param['geo_sel'])]

df_com = df_com.reset_index(drop=True)

l_depcom    = df_com["DEPCOM"]
l_comweight = df_com["weight"]


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
                numpat=df_err['num_pat'][l_evt[p]]
                if evt['err']=='yob':
                    if evt['typ_err']=='null':
                        df_err.loc[df_err['num_pat']==numpat,'yob']=None
                    if evt['typ_err']=='':
                        df_err.loc[df_err['num_pat']==numpat,'yob']=2030
                        
                if evt['err']=='mob':
                    if evt['typ_err']=='null':
                        df_err.loc[df_err['num_pat']==numpat,'mob']=None
                    if evt['typ_err']=='':
                        df_err.loc[df_err['num_pat']==numpat,'mob']='99'    

                if evt['err']=='comm':
                    if evt['typ_err']=='null':
                        df_err.loc[df_err['num_pat']==numpat,'com']=None
                    if evt['typ_err']=='':
                        com=df_err['com'][l_evt[p]]
                        while com==df_err['com'][l_evt[p]]:
                            # tirage au sort de la commune
                            com=gen_com()  
                            
                        df_err.loc[df_err['num_pat']==numpat,'com']=com    

                        
                if evt['err']=='death':
                    if evt['typ_err']=='null':
                        df_err.loc[df_err['num_pat']==numpat,'death_dte']=None
                        df_err.loc[df_err['num_pat']==numpat,'death_ts']=None
                    if evt['typ_err']=='date':   
                        if pd.isnull(df_err['death_dte'][l_evt[p]]):
                            df_err.loc[df_err['num_pat']==numpat,'death_dte']=pd.to_datetime('2030-01-01', format="%Y-%m-%d")
                            df_err.loc[df_err['num_pat']==numpat,'death_ts']=47483
                        else:
                            df_err.loc[df_err['num_pat']==numpat,'death_dte']=pd.to_datetime(df_err['death_dte'][l_evt[p]])+datetime.timedelta(days=evt['err_sd'])
                            df_err.loc[df_err['num_pat']==numpat,'death_ts']=df_err['death_ts'][l_evt[p]]+evt['err_sd']                          
                if evt['err']=='mark':
                    if evt['typ_err']=='null':
                        df_err['mark_dte'][l_evt[p]]=None  
                        df_err['mark_ts'][l_evt[p]]=None  
                    if evt['typ_err']=='date':   
                        df_err['mark_dte'][l_evt[p]]=pd.to_datetime(df_err['mark_dte'][l_evt[p]])+datetime.timedelta(days=evt['err_sd'])
                        df_err['mark_ts'][l_evt[p]]=df_err['mark_ts'][l_evt[p]]+evt['err_sd']
                    if evt['typ_err']=='add': 
                        df_add=df_init.copy()
                        df_add['num_pat']=10000000+p
                        df_add['mark_dte']=pd.to_datetime(df_add['mark_dte'])+datetime.timedelta(days=evt['err_sd'])
                        df_add['mark_ts']=df_add['mark_ts']+evt['err_sd']
                        df_err=pd.DataFrame(df_add[df_add.index==[l_init_sel[p]]]).append(df_err, ignore_index=True) 
                    if evt['typ_err']=='del': 
                        df_err=df_err.drop([l_init_sel[p]])

                        

        df_err.to_csv(l_param["dir_err"]+file_name,index=False,sep=';')                

       