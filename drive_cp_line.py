# generation automatique de fichiers

import pandas as pd
import json
import datetime
import random
import sys
import os
import shutil
from pathlib import Path
import numpy as np
from scipy.stats import truncnorm

#################################################################################
comprefix="0"  # prefix to be added to 'commune' variable

timeorigin = pd.to_datetime('1900-01-01', format="%Y-%m-%d");

#################################################################################
# progress bar (https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console)
#################################################################################
# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

#################################################################################
# fonctions
#################################################################################

def gen_yob (age_mean,age_sd,ref_year):
     # attribution aleatoire de l'annee de naissance selon la fourchette des parametres
    #yob=ref_year-(random.randint(age_mean-age_sd,age_mean+age_sd))
    # yob=ref_year-int((random.gauss(age_mean, age_sd)))
    y=truncnorm((18 - age_mean) / age_sd, (90 - age_mean) / age_sd, loc=age_mean, scale=age_sd)
    year=y.rvs()
    yob=ref_year-int(year)
    
    return yob

################################################################################
def gen_mob ():
     # attribution aleatoire du mois de naissance
    l_month =['01','02','03','04','05','06','07','08','09','10','11','12']
    m = random.randint(0, len(l_month) - 1)  
    mob = l_month[m]  
    
    return mob

################################################################################
def gen_com():
    # attribution aleatoire ponderee (cf. recensement (weight)) de la commune de residence
    # selon le niveau geo
    com = random.choices(l_depcom,l_comweight)[0]
 
    com = comprefix + com;
    
    return com

# ################################################################################
def gen_events_init_lin (init_dte,occ,yn_occ,delay_mean,mark,end_dte):
    l_evt_dte=[]
    if yn_occ==1:
    # generation de la liste des dates d'evt possibles
        if occ==1:
            end_dte2=min(init_dte+datetime.timedelta(days=delay_mean),end_dte)
            l_evt_dte = pd.date_range(init_dte, end_dte2).tolist()
        else:
            begin_dte=max(init_dte-datetime.timedelta(days=delay_mean),deb)
            l_evt_dte = pd.date_range(begin_dte,init_dte).tolist()
                       
        evt_dte = random.choice(l_evt_dte)
    else:
        evt_dte=None
       
    new_evt=[mark,evt_dte]

    return new_evt

# ################################################################################
def gen_events_lin (yn_occ,mark,end_dte):

    if yn_occ==1:
    # generation de la liste des dates d'evt possibles
        l_evt_dte = pd.date_range(deb, end_dte).tolist()                     
        evt_dte = random.choice(l_evt_dte)
    else:
        evt_dte=None
       
    new_evt=[mark,evt_dte]
        
    return new_evt

################################################################################
# generation d'un nouveau patient malade
def gen_new_pat_init (num_pat,sex,age_mean,age_sd,ref_year,delay_death):
    
    # tirage au sort l'annee de naissance
    yob=gen_yob(age_mean,age_sd,ref_year)
    # tirage au sort du mois de naissance
    mob=gen_mob()
    # tirage au sort de la commune
    com=gen_com()    
    # tirage au sort de la date de l'event initial
    init_dte = random.choice(l_date)
    # Date de deces oui/non
    death=y_n_death[0]
    # tirage au sort de la date de dc
    if death==1:
        # generation de la liste des dates de dc possibles 
        end1_dte=min(init_dte+datetime.timedelta(days=delay_death),fin)
        l_death_dte = pd.date_range(init_dte, end1_dte).tolist()
        death_dte = random.choice(l_death_dte)
        end_dte=min(end1_dte,death_dte)
    else:
        death_dte=None
        end_dte=fin
    
    # generation des events
    evt_pat=[]
    new_pat=[]
    for e, evt in enumerate(l_event):
        if l_y_n_init[e][0]==1:
            for o in range (random.randint(evt['nb_occ'], evt['nb_occ_max'])):
                new_evt=gen_events_init_lin(init_dte,evt['occ'],l_y_n_init[e][0],evt['delay_mean'],evt['mark'],end_dte)
                new_pat= [num_pat+param['first_num_pat'],sex,yob,mob,com,init_dte,death,death_dte]+new_evt
                evt_pat.append(new_pat)
            
        del l_y_n_init[e][0]

    new_pat= [num_pat+param['first_num_pat'],sex,yob,mob,com,init_dte,death,death_dte,l_init['mark'],init_dte]
    evt_pat.append(new_pat)
    return evt_pat

################################################################################
# generation d'un nouveau patient non malade
def gen_new_pat (num_pat,sex,age_mean,age_sd,ref_year):
    
    # tirage au sort l'annee de naissance
    yob=gen_yob(age_mean,age_sd,ref_year)
    # tirage au sort du mois de naissance
    mob=gen_mob()
    # tirage au sort de la commune
    com=gen_com()    

    # tirage au sort de la date de l'event initial
    init_dte=None
    
    # Date de deces : selon proba
    death=y_n_death[0]
    # tirage au sort de la date de dc
    if death==1:
        # generation de la liste des dates de dc possibles 
        l_death_dte = pd.date_range(deb, fin).tolist()
        death_dte = random.choice(l_death_dte)
        end_dte=death_dte
    else:
        death_dte=None
        end_dte=fin
    
    # generation des events
    evt_pat=[]
    new_pat=[]
    for e,evt in enumerate(l_event):
        if l_y_n[e][0]==1:
            for o in range (random.randint(evt['nb_occ'], evt['nb_occ_max'])):
                new_evt=gen_events_lin(l_y_n[e][0],evt['mark'],end_dte)
                new_pat= [num_pat+param['first_num_pat'],sex,yob,mob,com,init_dte,death,death_dte]+new_evt
                evt_pat.append(new_pat) 
        
        del l_y_n[e][0]

    new_pat= [num_pat+param['first_num_pat'],sex,yob,mob,com,init_dte,death,death_dte,'INIT',init_dte]
    evt_pat.append(new_pat)         
    return evt_pat

#################################################################################
# debut programme
#################################################################################

if len(sys.argv)<1:
    print ("You must provide :")
    print ("   1) [IN]  a json parameter file")
    sys.exit();

file_param = sys.argv[1];

# lecture du fichiers des parametres generaux
f_param = json.load(open(file_param))

param   = f_param['parameters']
l_init  = f_param['init']
l_event = f_param['events']

# if no output directory is defined, we create one in the current folder
if not "rep_file" in param: 
    base = Path(file_param).stem;
    outputDir = "run_" + base + "_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print ("no 'rep_file' defined -> creating directory", outputDir);
    os.mkdir (outputDir); 
    param["rep_file"] = outputDir + "/"

if not param["rep_file"].endswith("/"):  param["rep_file"] += "/"

# we also copy the configuration file in the output directory
shutil.copy(file_param, param["rep_file"] + os.path.basename(file_param));

file_all     = param.get("file_all",     "file_all.csv")
file_init    = param.get("file_init",    "file_init.csv")
file_healthy = param.get("file_healthy", "file_healthy.csv")

# we initialize the random generator by a seed (if any provided by the user)
# by default, a 0 seed is used which ensures that the outputs are the same for the same config.
seed = param.get("seed", "0")
random.seed (int(seed));
np.random.seed (int(seed));

if 'first_num_pat' not in param:  param['first_num_pat'] = 0;

# recuperation des parametres demographique
nb_men_init   = int(param['pop']*param['pct_men']*param['pct_ill'])
nb_men        = int(param['pop']*param['pct_men'])-nb_men_init

nb_women_init = int(param['pop']*param['pct_ill']) - nb_men_init
nb_women      = param['pop']-int(param['pop']*param['pct_ill']) - nb_men

deb = datetime.datetime.strptime(param['begin_dte'],'%Y-%m-%d') 
fin = datetime.datetime.strptime(param['end_dte'],  '%Y-%m-%d') 

delay_death_m = l_init['delay_death_m']*365
delay_death_w = l_init['delay_death_w']*365

# generation de la liste des dates de la periode d'etude
l_date = pd.date_range(param['begin_dte'], param['end_dte']).tolist()


# constitution du dataframe geo correspondant aux paramètres choisis
# tirage au sort de la commune au niveau de la Fr, d'une région ou d'un departement
if param['geo_level']=='fr':
    header_row = ['DEPCOM', 'DEP', 'REG', 'PTOT', 'weight', 'weight_reg', 'weight_dep']
    df=pd.read_csv(filepath_or_buffer='data_ref/communes_fr.csv',sep=';', header=0, names=header_row)
    df_com=df

elif param['geo_level']=='reg':
    header_row = ['DEPCOM', 'DEP', 'REG', 'PTOT', 'weight_fr', 'weight', 'weight_dep']
    df=pd.read_csv(filepath_or_buffer='data_ref/communes_fr.csv',sep=';',header=0, names=header_row)
    df_com=df[(df['REG']==param['geo_sel'])]

elif param['geo_level']=='dep':
    header_row = ['DEPCOM', 'DEP', 'REG', 'PTOT', 'weight_fr', 'weight_reg', 'weight']
    df=pd.read_csv(filepath_or_buffer='data_ref/communes_fr.csv',sep=';', header=0, names=header_row)
    df_com=df[(df['DEP']==param['geo_sel'])]

df_com = df_com.reset_index(drop=True)

l_depcom    = df_com["DEPCOM"]
l_comweight = df_com["weight"]

# liste 0/1 (pct de patient malades) par evt pour les patients "init"
# permet de maitriser le nb exact d'evt et donc respecter les parametres  
l_y_n_init=[]
for e in l_event:
    y_n = [0]*((nb_men_init+nb_women_init)-int(e['pct_occ']*(nb_men_init+nb_women_init))) + [1]*int(e['pct_occ']*(nb_men_init+nb_women_init))
    random.shuffle(y_n)
    l_y_n_init.append(y_n)

# liste 0/1 (pct de patient non malades) par evt pour les patients "sains"
l_y_n=[]
for e in l_event:
    y_n = [0]*((nb_men+nb_women)-int(e['pct_occ_pop']*(nb_men+nb_women))) + [1]*int(e['pct_occ_pop']*(nb_men+nb_women))
    random.shuffle(y_n)
    l_y_n.append(y_n)
    
# ################################################################################
# generation fichier patients
# ################################################################################

# generation de la population des hommes malades
l_men_init=[]
y_n_death = [0]*(nb_men_init-int(l_init['pct_death_m']*nb_men_init)) + [1]*int(l_init['pct_death_m']*nb_men_init)
random.shuffle(y_n_death)

for i in range(nb_men_init):
    new_pat_init=gen_new_pat_init(i+1,1,l_init['age_mean_m'],l_init['age_sd_m'],param['ref_year'],delay_death_m)

    for e,evt in enumerate(new_pat_init):
        l_men_init.append(new_pat_init[e])
       
    del y_n_death[0]
    
    printProgressBar(i, nb_men_init-1, prefix="men   (ill)", length=50)

# generation de la population des femmes malades 
l_women_init=[]
y_n_death = [0]*(nb_women_init-int(l_init['pct_death_w']*nb_women_init)) + [1]*int(l_init['pct_death_w']*nb_women_init)
random.shuffle(y_n_death)
[i0,i1] = [nb_men_init,int(param['pop']*param['pct_ill'])]
for j in range(i0,i1):
    new_pat_init=gen_new_pat_init(j+1,2,l_init['age_mean_w'],l_init['age_sd_w'],param['ref_year'],delay_death_m)

    for e,evt in enumerate(new_pat_init):
        l_women_init.append(new_pat_init[e])

    del y_n_death[0]
    
    printProgressBar(j-i0, i1-i0-1, prefix="women (ill)", length=50)

# generation de la population des hommes sans la maladie initiale
l_men=[]
y_n_death = [0]*(nb_men-int(param['pct_death_m_pop']*nb_men)) + [1]*int(param['pct_death_m_pop']*nb_men)
random.shuffle(y_n_death)
[i0,i1] = [nb_women_init+nb_men_init, nb_men+int(param['pop']*param['pct_ill'])]
for k in range(i0,i1):
    new_pat = gen_new_pat(k+1,1,int(param['age_mean_m']),int(param['age_sd_m']),param['ref_year'])

    for e,evt in enumerate(new_pat):  
        l_men.append(new_pat[e])
        
    del y_n_death[0]

    printProgressBar(k-i0, i1-i0-1, prefix="men        ", length=50)

# generation de la population des femmes sans la maladie initiale 
l_women=[]
y_n_death = [0]*(nb_women-int(param['pct_death_w_pop']*nb_women)) + [1]*int(param['pct_death_w_pop']*nb_women)
random.shuffle(y_n_death)
[i0,i1] = [nb_women_init+nb_men_init+nb_men, param['pop']]
for l in range(i0,i1):
    new_pat=gen_new_pat(l+1,2,param['age_mean_w'],param['age_sd_w'],param['ref_year'])
        
    for e,evt in enumerate(new_pat): 
        l_women.append(new_pat[e])
        
    del y_n_death[0]

    printProgressBar(l-i0, i1-i0-1, prefix="women      ", length=50)

# preparation export csv, selon format
col_evt=[]

col_exp    = ['num_pat', 'sex','yob','mob','com',l_init["mark"],'death','death_dte', 'mark','mark_dte']  
col_exp_pat= ['num_pat', 'sex','yob','mob','com',l_init["mark"],'death','death_dte']  
col_exp_evt= ['num_pat', 'mark','mark_dte']  

df_all     = pd.DataFrame(data=l_men_init+l_women_init+l_men+l_women,columns =col_exp)  
df_pat_all = df_all.drop(['mark','mark_dte'] ,axis=1)
df_pat_all = df_pat_all.drop_duplicates()

df_evt_all = df_all.dropna(subset=['mark_dte'])
df_evt_all = df_evt_all.drop(['sex','yob','mob','com',l_init["mark"],'death','death_dte'] ,axis=1)
df_all     = pd.merge(df_pat_all,df_evt_all,on='num_pat',how='left')
df_all     = df_all.drop(l_init["mark"] ,axis=1)    

df_all["death_ts"] = (pd.to_datetime(df_all["death_dte"], format="%Y-%m-%d")-pd.to_datetime('1900-01-01', format="%Y-%m-%d")).dt.days
df_all["mark_ts"]  = (pd.to_datetime(df_all["mark_dte"], format="%Y-%m-%d")-pd.to_datetime('1900-01-01', format="%Y-%m-%d")).dt.days
df_all["birth_ts"] = (pd.to_datetime(df_all["yob"].map(str)+df_all["mob"].map(str)+'01', format="%Y%m%d")-pd.to_datetime('1900-01-01', format="%Y-%m-%d")).dt.days

df_init     = pd.DataFrame(data=l_men_init+l_women_init,columns =col_exp)   
df_pat_init = df_init.drop(['mark','mark_dte'] ,axis=1)
df_pat_init = df_pat_init.drop_duplicates()

df_evt_init = df_init.dropna(subset=['mark_dte'])
df_evt_init = df_evt_init.drop(['sex','yob','mob','com',l_init["mark"],'death','death_dte'] ,axis=1)
df_init     = pd.merge(df_pat_init,df_evt_init,on='num_pat',how='left')
df_init     = df_init.drop(l_init["mark"] ,axis=1)    

df_init["death_ts"] = (pd.to_datetime(df_init["death_dte"], format="%Y-%m-%d")-timeorigin).dt.days
df_init["mark_ts"]  = (pd.to_datetime(df_init["mark_dte"],  format="%Y-%m-%d")-timeorigin).dt.days
df_init["birth_ts"] = (pd.to_datetime(df_init["yob"].map(str)+df_init["mob"].map(str)+'01', format="%Y%m%d")-timeorigin).dt.days

df_healthy     = pd.DataFrame(data=l_men+l_women,columns =col_exp)
df_pat_healthy = df_healthy.drop(['mark','mark_dte'] ,axis=1)
df_pat_healthy = df_pat_healthy.drop_duplicates()

df_evt_healthy = df_healthy.dropna(subset=['mark_dte'])
df_evt_healthy = df_evt_healthy.drop(['sex','yob','mob','com',l_init["mark"],'death','death_dte'] ,axis=1)
df_healthy     = pd.merge(df_pat_healthy,df_evt_healthy,on='num_pat',how='left')
df_healthy     = df_healthy.drop(l_init["mark"] ,axis=1)    

df_healthy["death_ts"] = (pd.to_datetime(df_healthy["death_dte"], format="%Y-%m-%d")-timeorigin).dt.days
df_healthy["mark_ts"]  = (pd.to_datetime(df_healthy["mark_dte"],  format="%Y-%m-%d")-timeorigin).dt.days
df_healthy["birth_ts"] = (pd.to_datetime(df_healthy["yob"].map(str)+df_healthy["mob"].map(str)+'01', format="%Y%m%d")-timeorigin).dt.days

# export de la population dans un fichier csv
df_all.    to_csv (param["rep_file"]+ file_all,     index=False, sep=';')
df_init.   to_csv (param["rep_file"]+ file_init ,   index=False, sep=';')
df_healthy.to_csv (param["rep_file"]+ file_healthy, index=False, sep=';')
