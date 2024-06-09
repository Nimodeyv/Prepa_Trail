

from geopy import distance
import pandas as pd
import datetime
from math import sqrt
import re
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches
import seaborn as sns

from selenium import webdriver
from selenium.webdriver.common.by import By
# import chromedriver_autoinstaller
# from selenium.webdriver.support import expected_conditions
# from selenium.webdriver.support.ui import WebDriverWait
from sklearn.model_selection import train_test_split
# from sklearn.pipeline import make_pipeline
# from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn import linear_model

import folium
import folium.plugins as plugins

from IPython.display import display


################################################################################################

def distance_with_altitude(latitude1, longitude1, altitude1, latitude2, longitude2, altitude2):
    flat_distance = distance.distance((latitude1, longitude1), (latitude2, longitude2)).m
    euclidian_distance = sqrt(flat_distance**2 + (altitude2 - altitude1)**2)
    return euclidian_distance

##############################################################################################


# CLASS TRAIL 


################################################################################################

class Trail:
    def __init__(self,nom_id,d,s,hd,csv, mod):
        self.nom_id = nom_id 
        self.date = d
        self.suivi = s
        self.heure_depart = hd
        self.csv_file = csv
        self.modele_pred = mod
        

################################################################################################

    def load_ppassage_csv(self):
        self.df_ppassage = pd.read_csv(f'./data/ppassages/{self.csv_file}',sep=';')
        self.df_ppassage.loc[0,'Delta_reel_h']=0.0
        self.df_ppassage.loc[0,'Delta_Dist_km']=0
        self.df_ppassage.loc[0,'Delta_D+_m']=0
        for i in range(len(self.df_ppassage)-1):
            self.df_ppassage.loc[i+1,'Delta_reel_h']=self.df_ppassage.loc[i+1,'H_reel_h']-self.df_ppassage.loc[i,'H_reel_h']
            self.df_ppassage.loc[i+1,'Delta_Dist_km']=self.df_ppassage.loc[i+1,'Cumul_Dist_km']-self.df_ppassage.loc[i,'Cumul_Dist_km']
            self.df_ppassage.loc[i+1,'Delta_D+_m']=self.df_ppassage.loc[i+1,'Cumul_D+_m']-self.df_ppassage.loc[i,'Cumul_D+_m']
        # display(self.df_ppassage)
        print(f'CSV File loaded under {self.nom_id}.df_ppassage')
    

################################################################################################

    def remove_missing(self): # Elimine les empty cell et corrige s'il manque une heure de passage 
        if self.df_ppassage['Heure_Passage'].isnull().values.any():
            print('Il y a une heure de passage manquante',self.df_ppassage[self.df_ppassage['Heure_Passage'].isnull()]['Point_passage'])
            self.df_ppassage=self.df_ppassage.dropna(axis=0,subset=['Heure_Passage']).reset_index(drop=True)
            for i in range(1,len(self.df_ppassage)):             
                self.df_ppassage.loc[i,'Delta_Dist_km']=self.df_ppassage.loc[i,'Cumul_Dist_km']-self.df_ppassage.loc[i-1,'Cumul_Dist_km']
                self.df_ppassage.loc[i,'Delta_D+_m']=self.df_ppassage.loc[i,'Cumul_D+_m']-self.df_ppassage.loc[i-1,'Cumul_D+_m'] 
    

################################################################################################


    def load_gpx(self, file):
        with open(file) as f:
            data=f.read().strip()
            data_parse =data.split('<trkpt')
            #utb_lst_elev = []
            parcours=[]
            for p in data_parse[1:]:
                pt={}
                try:
                    pt['Altitude_m'] = float(re.findall('<ele>(.+?)</ele>', p, re.DOTALL)[0])
                except:
                    pt['Altitude_m']='NA'
                try:
                    pt['Heure_Passage'] = re.findall('<time>(.+?)</time>', p, re.DOTALL)[0]
                    # Convert Heure_Passage to datetime UTC+1
                    pt['Heure_Passage'] = pd.to_datetime(pt['Heure_Passage'])+pd.Timedelta(hours=2) # UTC+2 for summer
                except:
                    pt['Heure_Passage']='NA'
                try:
                    pt['hr'] = int(re.findall('<ns3:hr>(.+?)</ns3:hr>', p, re.DOTALL)[0])
                    pt['cad'] = int(re.findall('<ns3:cad>(.+?)</ns3:cad>', p, re.DOTALL)[0])
                except:
                    pt['hr']='NA'
                    pt['cad']='NA'
                pt['lat'] = float(re.findall('"(.+?)"',p)[0])
                pt['lon'] = float(re.findall('"(.+?)"',p)[1])
                # print(pt)
                parcours.append(pt)
        
        self.df_parcours = pd.DataFrame(parcours)

        # If 'NA' in Altitude_m, on prend la valeur du point précédent
        counter = 0
        for i in range(1, len(self.df_parcours)):
            # print(self.df_parcours.loc[i,'Altitude_m'])
            if self.df_parcours.loc[i,'Altitude_m']=='NA':
                try:
                    self.df_parcours.loc[i,'Altitude_m']=self.df_parcours.loc[i-1,'Altitude_m']
                    counter += 1
                except:
                    print('Erreur d interpolation de l altitude')
        print((f'{counter} points ont été interpolés pour l altitude'))

        if self.nom_id != 'All':
            # Calculate distance between 2 points lat and lon of df_parcours
            self.df_parcours['Delta_Dist_m']=0
            for i in range(1,len(self.df_parcours)):
                # self.df_parcours.loc[i,'Delta_Dist_m']=geodesic((self.df_parcours.loc[i-1,'lat'],self.df_parcours.loc[i-1,'lon']),(self.df_parcours.loc[i,'lat'],self.df_parcours.loc[i,'lon'])).meters
                # self.df_parcours.loc[i,'Delta_Dist_m'] = getDistanceBetweenPointsNew(latitude1 = self.df_parcours.loc[i-1,'lat'], 
                #                                                                      longitude1= self.df_parcours.loc[i-1,'lon'], 
                #                                                                      latitude2 = self.df_parcours.loc[i,'lat'], 
                #                                                                      longitude2 = self.df_parcours.loc[i,'lon'], 
                #                                                                      unit = 'meters')
                # self.df_parcours.loc[i,'Delta_Dist_m'] = distance(s_lat = self.df_parcours.loc[i-1,'lat'], 
                #                                                                      s_lng= self.df_parcours.loc[i-1,'lon'], 
                #                                                                      e_lat = self.df_parcours.loc[i,'lat'], 
                #                                                                      e_lng = self.df_parcours.loc[i,'lon'], 
                #                                                                      )
                self.df_parcours.loc[i,'Delta_Dist_m'] = distance_with_altitude(latitude1 = self.df_parcours.loc[i-1,'lat'], 
                                                                                     longitude1= self.df_parcours.loc[i-1,'lon'], 
                                                                                     altitude1 = self.df_parcours.loc[i-1,'Altitude_m'],
                                                                                     latitude2 = self.df_parcours.loc[i,'lat'], 
                                                                                     longitude2 = self.df_parcours.loc[i,'lon'], 
                                                                                    altitude2 = self.df_parcours.loc[i,'Altitude_m'],
                                                                                    )   


            # Convert time to datetime
            self.df_parcours['Heure_Passage']=pd.to_datetime(self.df_parcours['Heure_Passage'])
            # Calcule delta time in sec between 2 points
            self.df_parcours['Delta_reel_s']=0
            for i in range(1,len(self.df_parcours)):
                self.df_parcours.loc[i,'Delta_reel_s']=(self.df_parcours.loc[i,'Heure_Passage']-self.df_parcours.loc[i-1,'Heure_Passage']).seconds
            # Calculate delta alt in m between 2 points
            self.df_parcours['Dénivelé_m']=0
            try:
                for i in range(1,len(self.df_parcours)):
                    self.df_parcours.loc[i,'Dénivelé_m']=(self.df_parcours.loc[i,'Altitude_m']-self.df_parcours.loc[i-1,'Altitude_m'])
            except:
                print('Probleme avec l altitude')
            # Calculate D+ and D- 
            self.df_parcours['Delta_D+_m']=self.df_parcours['Dénivelé_m'].apply(lambda x: x if x>0 else 0)
            self.df_parcours['Delta_D-_m']=self.df_parcours['Dénivelé_m'].apply(lambda x: x if x<0 else 0)

        print(f'gpx File loaded under {self.nom_id}.df_parcours')
         

################################################################################################

    def load_data_livetrail(self,url, coureur): # Format heure depart XX:XX:XX
        # OLD install chrome web driver https://sites.google.com/a/chromium.org/chromedriver/downloads
        # OLD PATH = "C:\Program Files\chromedriver.exe"
        # options = webdriver.ChromeOptions()
        # driver = webdriver.Chrome('C:/Users/nimod/.conda/envs')
        driver = webdriver.Firefox()
        # driver = webdriver.Chrome(service=webdriver.chrome.service.Service(executable_path='C:/Users/nimod/.conda/envs'), options=chrome_options)
        # PATH = "C:/Program Files/chromedriver.exe"
        # driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(1)
        inputElement = driver.find_element(By.NAME, "rech")
        inputElement.send_keys(coureur)
        inputElement.submit()
        time.sleep(10) # Mettre 2 si le temps est trop long, sinon cliquer manuellement si 2 noms apparaissent par exemple
        tableau = driver.find_element(By.XPATH, '//*[@id="fc"]/div[3]/div[2]/a[1]')
        tableau.click()
        txt = driver.page_source
        txt = txt.replace('&nbsp;','').replace('\n','').replace('\t','')
        time.sleep(2)
        driver.close()
        # Extract 
        inter = re.findall('idpt:(.+?){',txt,re.DOTALL)
        table =[]
        for l in inter:
            point={}
            #print(l)
            point['id']= int(re.findall("'(.+?)',kmt",l,re.DOTALL)[0])
            point['Point_passage']=re.findall('n:"(.+?)"',l,re.DOTALL)[0]
            point['Altitude_m']=int(re.findall("a:'(.+?) m'",l,re.DOTALL)[0].replace(' ','').replace(',',''))
            point['Cumul_Dist_km']=float(re.findall("kmt:'(.+?) km'",l,re.DOTALL)[0].replace(',','.'))
            if 'NaN' in re.findall("kmp:'(.+?) km'",l,re.DOTALL)[0]:
                point['Delta_Dist_km']=0.0
            else:
                point['Delta_Dist_km']=float(re.findall("kmp:'(.+?) km'",l,re.DOTALL)[0].replace(',','.'))
            point['Cumul_D+_m']=int(re.findall("dt:'(.+?) m'",l,re.DOTALL)[0].replace(' ','').replace(',',''))
            try: point['Delta_D+_m']=int(re.findall("dp:'(.+?) m'",l,re.DOTALL)[0].replace(' ','').replace(',','')) 
            except: point['Delta_D+_m']=0
            point['lon']=float(re.findall("lon:'(.+?)'",l,re.DOTALL)[0])
            point['lat']=float(re.findall("lat:'(.+?)'",l,re.DOTALL)[0])
            try: 
                point['Heure_Passage']=(re.findall("hp:'(.+?)',tc",l,re.DOTALL)[0])
                if '<br/>' in point['Heure_Passage']:
                    point['Heure_Passage'] = point['Heure_Passage'].split('<br/>')[0]
            except: point['Heure_Passage']=None
            try: point['Temps_course']=(re.findall("tc:'(.+?)',clt",l,re.DOTALL)[0])
            except: point['Temps_course']=''
            try: point['Classement']=(re.findall("clt:'(.+?)',vit",l,re.DOTALL)[0])
            except: point['Classement']=''
            try: point['Vitesse_km/h']=float(re.findall("vit:'(.+?)km/h'",l,re.DOTALL)[0].replace(',','.')) 
            except: point['Vitesse_km/h']=0
            #print(point)
            table.append(point)
        self.df_ppassage=pd.DataFrame(table)
        # Drop rows when 'Heure_Passage' is none
        self.df_ppassage = self.df_ppassage.dropna(subset=['Heure_Passage']).reset_index(drop=True)
        # Conversion des données
        for i in range(len(self.df_ppassage)):
            try:
                self.df_ppassage.loc[i,'H_reel_h']=int(self.df_ppassage.loc[i,'Temps_course'].split(':')[0])+int(self.df_ppassage.loc[i,'Temps_course'].split(':')[1])/60+int(self.df_ppassage.loc[i,'Temps_course'].split(':')[2])/60/60
            except:
                 self.df_ppassage.loc[i,'H_reel_h']=0
        self.df_ppassage.loc[0,'Delta_reel_h']=0
        for i in range(len(self.df_ppassage)-1):
            self.df_ppassage.loc[i+1,'Delta_reel_h']=self.df_ppassage.loc[i+1,'H_reel_h']-self.df_ppassage.loc[i,'H_reel_h']
        # Enregistrement
        self.csv_file = self.date+"_"+re.findall(coureur+'-(.+?)- Live',txt,re.DOTALL)[0].strip()+"_"+str(self.df_ppassage.loc[len(self.df_ppassage)-1,'Cumul_Dist_km'])+"km.csv"
        self.df_ppassage.to_csv(f'./data/{self.csv_file}', index=False, sep=';')
        print('Livetrail data loaded under XXX.df_ppassage and .csv file')
    

################################################################################################

    def load_data_before_livetrack(self, url): # # Format heure depart XX:XX:XX
        # install chrome web driver https://sites.google.com/a/chromium.org/chromedriver/downloads
        # PATH = "C:/Program Files/chromedriver.exe"
        # driver = webdriver.Chrome()
        driver = webdriver.Firefox()
        driver.get(url)
        time.sleep(1)
        txt = driver.page_source
        time.sleep(2)
        driver.close()
        # Extract 
        inter = re.findall('<tbody>(.+?)</tbody>',txt,re.DOTALL)[0]
        inter2 = re.findall('<tr (.+?)</tr>',inter,re.DOTALL)
        table =[]
        for l in inter2:
            point={}
            # print(l)
            point['id']= int(re.findall('class="sequenceNumber">(.+?)</span>',l,re.DOTALL)[0])
            point['Point_passage']=re.findall('class="stationName">(.+?)</span>',l,re.DOTALL)[0]

            point['Delta_Dist_km']=float(re.findall('class="right aligned separated">(.+?)</td>',l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ',''))
            point['Cumul_Dist_km']=float(re.findall('class="right aligned separated">(.+?)</td>',l,re.DOTALL)[1].replace('k','').replace('m','').replace(' ',''))
            
            if 'km' in re.findall('class="right aligned separated">(.+?)</td>',l,re.DOTALL)[0]:
                point['Delta_Dist_km']=float(re.findall('class="right aligned separated">(.+?)</td>',l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ',''))
            else:
                point['Delta_Dist_km']=float(re.findall('class="right aligned separated">(.+?)</td>',l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ',''))/1000
                
            point['Cumul_Dist_km']=float(re.findall('class="right aligned separated">(.+?)</td>',l,re.DOTALL)[1].replace('k','').replace('m','').replace(' ',''))
            
            point['Delta_D+_m']=int(re.findall('class="right aligned">D(.+?) m</td>',l,re.DOTALL)[0].replace('+ ',''))
            point['Delta_D-_m']=int(re.findall('class="right aligned">D(.+?) m</td>',l,re.DOTALL)[1].replace('- ',''))

            point['Cumul_D+_m']=int(re.findall('class="right aligned">D(.+?) m</td>',l,re.DOTALL)[2].replace('+ ',''))
            point['Cumul_D-_m']=int(re.findall('class="right aligned">D(.+?) m</td>',l,re.DOTALL)[3].replace('- ',''))#     except: point['Delta_D+_m']=0

            Missing_info = '"sequence_number":'+str(point['id'])+'(.+?){"id":'
            new_l=re.findall(Missing_info,txt,re.DOTALL)[0]
            point['lon']=float(re.findall('gps_longitude":(.+?),"gps',new_l,re.DOTALL)[0])
            point['lat']=float(re.findall('gps_latitude":(.+?),"gps',new_l,re.DOTALL)[0])
            point['Altitude_m']=int(float(re.findall('gps_elevation":(.+?),"is_public"',new_l,re.DOTALL)[0]))
            table.append(point)
        table
        self.df_ppassage=pd.DataFrame(table)
        # self.df_ppassage.loc[0,'Heure_Passage']=self.heure_depart
        # for i in range(len(self.df_ppassage)):
        #     try:
        #         self.df_ppassage.loc[i,'H_reel_h']=int(self.df_ppassage.loc[i,'Temps_course'].split(':')[0])+int(self.df_ppassage.loc[i,'Temps_course'].split(':')[1])/60+int(self.df_ppassage.loc[i,'Temps_course'].split(':')[2])/60/60
        #     except:
        #          self.df_ppassage.loc[i,'H_reel_h']=0
        # # Enregistrement
        self.csv_file = self.date+"_"+re.findall('LiveTrack(.+?)-',txt,re.DOTALL)[0].replace('|','').strip()+"_"+str(self.df_ppassage.loc[len(self.df_ppassage)-1,'Cumul_Dist_km'])+"km.csv"
        self.df_ppassage.to_csv(f'./data/{self.csv_file}', index=False)
        print('Livetrail data loaded under XXX.df_ppassage and .csv file')    
    

################################################################################################

    def load_data_after_livetrack(self, url, coureur): # 
        print('Vérifier que la method .load_data_before_livetrack a déjà été exécutée')
        # coureur ='romain-morand' 
        url = url.replace('course','coureur')+'-'+coureur
        # install chrome web driver https://sites.google.com/a/chromium.org/chromedriver/downloads
        # PATH = "C:/Program Files/chromedriver.exe"
        driver = webdriver.Chrome()
        driver.get(url)
        time.sleep(1)
        # Chargement des données avec temps de passage par défaut
        txt = driver.page_source   
        time.sleep(2)
        # Extract 
        inter = re.findall('<tbody>(.+?)</tbody>',txt,re.DOTALL)[0]
        inter2 = re.findall('<tr (.+?)</tr>',inter,re.DOTALL)
        table =[]
        for l in inter2:
            point={}
            # print(l)
            point['id']= int(re.findall('class="sequenceNumber">(.+?)</span>',l,re.DOTALL)[0])
            point['Point_passage']=re.findall('class="stationName">(.+?)</span>',l,re.DOTALL)[0]
            infos = re.findall('class="center aligned">(.+?)</td>',l,re.DOTALL)[0].split('/')
            # if 'km' in infos[0]:
            #     point['Cumul_Dist_km']=float(infos[0].replace('km',''))
            # else:
            #     point['Cumul_Dist_km']=float(infos[0].replace('m',''))/1000
            # point['Cumul_D+_m']=float(infos[1].replace('D+','').replace('m',''))
            try: point['Heure_Passage']=re.findall('<span class="timestamp">(.+?)</span>',l,re.DOTALL)[0]
            except: point['Heure_Passage']=''
            if 'Pause' in l:
                point['Temps_pause']=re.findall('<span class="timestamp">(.+?)</span>',l,re.DOTALL)[1]
            try: point['Classement']=(re.findall('<span class="ranking">(.+?)</span>',l,re.DOTALL)[0])
            except: point['Classement']=''
            table.append(point)
        df=pd.DataFrame(table)
        # Switch pour les temps de course au lieu du temps de passage
        checkbox = driver.find_elements(By.XPATH, "//label[@for='showRaceTimes']")
        print(checkbox)
        checkbox[0].click()
        time.sleep(1)
        txt = driver.page_source 
        time.sleep(1)
        # Extract 
        inter = re.findall('<tbody>(.+?)</tbody>',txt,re.DOTALL)[0]
        inter2 = re.findall('<tr (.+?)</tr>',inter,re.DOTALL)
        table2 =[]
        for l in inter2:
            point={}
            point['Point_passage']=re.findall('class="stationName">(.+?)</span>',l,re.DOTALL)[0]
            try:point['Temps_course']=re.findall('<span class="timestamp">(.+?)</span>',l,re.DOTALL)[0]     
            except: point['Temps_course']=''
            table2.append(point)
        df2=pd.DataFrame(table2)
        df= pd.merge(df,df2,on='Point_passage',how='left')
        #
        for i in range(len(df)):
            try:
                df.loc[i,'H_reel_h']=int(df.loc[i,'Temps_course'].split(':')[0])+int(df.loc[i,'Temps_course'].split(':')[1])/60+int(df.loc[i,'Temps_course'].split(':')[2])/60/60
            except:
                 df.loc[i,'H_reel_h']=0  
        self.df_ppassage=pd.merge(self.df_ppassage,df,on='Point_passage',how='left')
        # Enregistrement
        titre = re.findall('<title>(.+?)</title>',txt,re.DOTALL)[0]
        self.csv_file = self.date+"_"+re.findall('-(.+?)-',titre,re.DOTALL)[0].replace('|','').strip()+"_"+str(self.df_ppassage.loc[len(self.df_ppassage)-1,'Cumul_Dist_km'])+"km.csv"
        self.df_ppassage.to_csv(f'./data/{self.csv_file}', index=False)
        print('Livetrail data loaded under XXX.df_ppassage and .csv file')    
        driver.close()
    
################################################################################################

    def arret(self, durée_stop, à_partir_de):
        self.df_ppassage['H_reel_h_init']=self.df_ppassage['H_reel_h']
        for i in range(len(self.df_ppassage)-1):
            if self.df_ppassage.loc[i+1,'H_reel_h']>à_partir_de:
                self.df_ppassage.loc[i+1,'H_reel_h']=self.df_ppassage.loc[i+1,'H_reel_h_init']-durée_stop
            else: 
                self.df_ppassage.loc[i+1,'H_reel_h']=self.df_ppassage.loc[i+1,'H_reel_h']
        # On recalcule de DeltaT
        self.df_ppassage['Delta_reel_h_init']=self.df_ppassage['Delta_reel_h']
        for i in range(len(self.df_ppassage)-1):
            self.df_ppassage.loc[i+1,'Delta_reel_h']=self.df_ppassage.loc[i+1,'H_reel_h']-self.df_ppassage.loc[i,'H_reel_h']

################################################################################################
    
    def load_data_before_livetrail(self, url): # # Format heure depart XX:XX:XX
        # options = webdriver.ChromeOptions()
        # driver = webdriver.Chrome(options=options)
        driver = webdriver.Firefox()
        driver.get(url)
        time.sleep(1)
        #
        txt = driver.page_source
        time.sleep(2)
        driver.close()
        # Extract 
        # inter = re.findall('<tbody>(.+?)</tbody>',txt,re.DOTALL)[0]
        # inter2 = re.findall('<tr (.+?)</tr>',inter,re.DOTALL)
        inter = re.findall('var pts_(.+?)];',txt,re.DOTALL)
        # print(inter)
        for c in inter:
            print(self.nom_id[4:].lower())
            # print(c)
            if (self.nom_id[4:].upper() in c) or (self.nom_id[4:].lower() in c): # Il faut que le nom du trail soit le meme que dans la recherche
                inter2 =re.findall('{marker(.+?)}',c,re.DOTALL)
                # print(inter2)
                table =[]
                for l in inter2:
                    point={}
                    # print(l)
                    point['id']= int(re.findall("idpt:'(.+?)',",l,re.DOTALL)[0])
                    # point['Point_passage_p']=re.findall('p:"(.+?)"',l,re.DOTALL)[0]
                    point['Point_passage']=re.findall('n:"(.+?)"',l,re.DOTALL)[0]
                    point['Delta_Dist_km']=float(re.findall("kmp:'(.+?)'",l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ','').replace(',','.'))
                    point['Cumul_Dist_km']=float(re.findall("kmt:'(.+?)'",l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ','').replace(',','.'))
        #             if 'km' in re.findall('class="right aligned separated">(.+?)</td>',l,re.DOTALL)[0]:
        #                 point['Delta_Dist_km']=float(re.findall('class="right aligned separated">(.+?)</td>',l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ',''))
        #             else:
        #                 point['Delta_Dist_km']=float(re.findall('class="right aligned separated">(.+?)</td>',l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ',''))/1000

        #             point['Cumul_Dist_km']=float(re.findall('class="right aligned separated">(.+?)</td>',l,re.DOTALL)[1].replace('k','').replace('m','').replace(' ','')
                    point['Delta_D+_m']=int(re.findall("dp:'(.+?)'",l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ','').replace(',','.'))
                    # point['Delta_D-_m']=int(re.findall('class="right aligned">D(.+?) m</td>',l,re.DOTALL)[1].replace('- ',''))
                    point['Cumul_D+_m']=int(re.findall("dt:'(.+?)'",l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ','').replace(',','.'))
                    # point['Cumul_D-_m']=int(re.findall('class="right aligned">D(.+?) m</td>',l,re.DOTALL)[3].replace('- ',''))#     except: point['Delta_D+_m']=0

        #             Missing_info = '"sequence_number":'+str(point['id'])+'(.+?){"id":'
        #             new_l=re.findall(Missing_info,txt,re.DOTALL)[0]
                    point['lon']=float(re.findall("lon:'(.+?)'",l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ','').replace(',','.'))
                    point['lat']=float(re.findall("lat:'(.+?)'",l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ','').replace(',','.'))
                    point['Altitude_m']=int(re.findall("a:'(.+?)'",l,re.DOTALL)[0].replace('k','').replace('m','').replace(' ','').replace(',','.'))
                    # print(point)
                    table.append(point)
        # print(table)
        self.df_ppassage=pd.DataFrame(table)
        self.df_ppassage['Temps_course']=0.0
        self.df_ppassage['Heure_Passage']='Not runned'
        self.df_ppassage['H_reel_h']=0
        self.df_ppassage['Delta_reel_h']=0
        self.df_ppassage['H_reel_h_init']=0
        self.df_ppassage['Temps_pause']=0
        self.df_ppassage['Delta_D-_m']='Not calculated'
        self.df_ppassage['Cumul_D-_m']='Not calculated'
        self.df_ppassage['Classement']='Not runned'
        self.df_ppassage['Heure_predite']='Not runned'
        display(self.df_ppassage)
        # self.df_ppassage= self.df_ppassage['Point_passage', 'Delta_Dist_km', 'Cumul_Dist_km', 'Delta_D+_m','Delta_D-_m', 'Cumul_D+_m', 'Cumul_D-_m', 'lon', 'lat', 'Altitude_m', 'Heure_Passage', 'Classement', 'Temps_pause', 'Temps_course', 'H_reel_h', 'Delta_reel_h']
        #
        # # Enregistrement
        self.csv_file = self.date+"_"+self.nom_id+"_"+str(self.df_ppassage.loc[len(self.df_ppassage)-1,'Cumul_Dist_km'])+"km.csv"
        self.df_ppassage.to_csv(f'./data/{self.csv_file}', index=False)
        print('Livetrail data loaded under XXX.df_ppassage and .csv file') 

    ################################################################################################
    
    def analyse2(self):  
        #
        reg = linear_model.LinearRegression(fit_intercept=False)
        y =np.array(self.df_ppassage.loc[(self.df_ppassage['Heure_Passage']!='Not yet there'),'Delta_reel_h'])
        X1 = np.array(self.df_ppassage.loc[(self.df_ppassage['Heure_Passage']!='Not yet there'),'Delta_Dist_km'])
        X2 = np.array(self.df_ppassage.loc[(self.df_ppassage['Heure_Passage']!='Not yet there'),'Delta_D+_m'])
        # X3 = np.array(df_ppassage['H_reel_h'])
        X= np.stack((X1,X2)).T
        reg.fit(X,y)
        fig1=plt.figure()
        # y =np.array(self.df_ppassage.loc[:,'Delta_reel_h'])
        # X1 = np.array(self.df_ppassage.loc[:,'Delta_Dist_km'])
        # X2 = np.array(self.df_ppassage.loc[:,'Delta_D+_m'])
        # X= np.stack((X1,X2)).T
        self.df_ppassage.loc[(self.df_ppassage['Heure_Passage']!='Not yet there'),'Pred_T_Rom']=reg.predict(X)
        levels, categories = pd.factorize(self.df_ppassage['Trail'])
        colors = [plt.cm.tab10(i) for i in levels] # using the "tab10" colormap
        handles = [matplotlib.patches.Patch(color=plt.cm.tab10(i), label=c) for i, c in enumerate(categories)]
        if len(y) < len(colors) : colors = colors[:len(y)]
        plt.scatter(y,self.df_ppassage.loc[(self.df_ppassage['Heure_Passage']!='Not yet there'),'Pred_T_Rom'],c=colors)
        plt.plot([0,np.max(y)],[0,np.max(y)])
        plt.grid()
        plt.xlabel('Durée segment reel (heure)')
        plt.ylabel('Durée segement predit (heure)')
        plt.legend(handles=handles,  title='Color')
        plt.show()
        print(reg.coef_)
        print('Regression score              :',round(reg.score(X, y),2))
        self.vit_plat = round(1/reg.coef_[0],1)
        print('Vitesse sur le plat (en km/h) :',round(self.vit_plat,1))
        self.vit_Dplus = round(1/reg.coef_[1],1)
        print('Vitesse en dénivelé (en m/h)  :',round(self.vit_Dplus,1), 'inverse (en h/1000m):', 1/self.vit_Dplus*1000)
        self.ralentissement = 0

    ################################################################################################

    def analyse3(self):
        #
        # reg = linear_model.LinearRegression(fit_intercept=False)
        # y =np.array(self.df_ppassage['Delta_reel_h'])
        # X1 = np.array(self.df_ppassage['Delta_Dist_km'])
        # X2 = np.array(self.df_ppassage['Delta_D+_m'])
        # X3 = np.array(self.df_ppassage['Cumul_Dist_km'])
        # X= np.stack((X1,X2,X3)).T
        # reg.fit(X,y)
    
        # Modélisation
        y = self.df_ppassage['Delta_reel_h']
        X = self.df_ppassage[['Delta_Dist_km','Delta_D+_m','Cumul_Dist_km']]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
        ridge_model = Ridge(alpha=1, fit_intercept=False)
        ridge_model.fit(X_train, y_train)

        self.vit_plat = round(1/ridge_model.coef_[0],2)
        self.vit_Dplus = int(1/ridge_model.coef_[1])
        self.ralentissement = round(ridge_model.coef_[2]*3600,2)
        self.fit_intercept = round(ridge_model.intercept_*3600,2)

        fig1=plt.figure()
        # plt.scatter(y,ridge_model.predict(X),c='blue')
        sns.scatterplot(x=y, y=ridge_model.predict(X), hue=self.df_ppassage['Trail'])
        plt.plot([0,np.max(y)],[0,np.max(y)],c='red')
        plt.grid()
        plt.title(f'{self.nom_id} - {self.date} - {self.heure_depart}')
        plt.xlabel('Durée segment reel (heure)')
        plt.ylabel('Durée segement predit (heure)')
        plt.show()
        
        print(f'{ridge_model.score(X_test, y_test)=}')
        print(f'{ridge_model.coef_=}')
        print(f'{ridge_model.intercept_=}')

        print('Vitesse sur le plat (en km/h)       :',round(self.vit_plat,1))
        print('Vitesse en dénivelé (en m/h)        :',round(self.vit_Dplus,1))
        print('Ralentissement (en sec ajoutée /km) :',round(self.ralentissement,2))
        print('Fit intercept (en sec)             :',round(self.fit_intercept,2))



    ################################################################################################

        
    def pred_temps(self, vit_plat,vit_Dplus,ralentissement,durée_stop,à_partir_de):
        print('Opti.: Vit_plat_km/h:',vit_plat,' | Vit_den+_m/h:', vit_Dplus,' | Ralent.:',ralentissement)
        df = self.df_ppassage
        df['Pred_Cum_T_Rom']=0 
        df['Pred_T_Rom']=0
        df['Pred_T_Rom']=round(df['Delta_Dist_km']/vit_plat+df['Delta_D+_m']/vit_Dplus+df['Cumul_Dist_km']*ralentissement,2)
        #
        df.loc[0,'Heure_predite']=(pd.to_datetime(f'{self.date} {self.heure_depart}').strftime("%a. %H:%M"))
        for i in range(1,len(df)):             
            df.loc[i,'Pred_Cum_T_Rom']=df.loc[i-1,'Pred_Cum_T_Rom']+df.loc[i,'Pred_T_Rom']
        for i in range(1,len(df)): 
            if df.loc[i,'Pred_Cum_T_Rom']>à_partir_de:
                df.loc[i,'Pred_Cum_T_Rom']=df.loc[i,'Pred_Cum_T_Rom']+durée_stop
            df.loc[i,'Heure_predite']=(pd.to_datetime(f'{self.date} {self.heure_depart}')+pd.Timedelta(hours=(df.loc[i,'Pred_Cum_T_Rom']//1), minutes= (df.loc[i,'Pred_Cum_T_Rom']%1*60))).strftime("%a. %H:%M")         
        df.loc[0,'Heure_predite']=pd.to_datetime(f'{self.date} {self.heure_depart}').strftime("%a. %H:%M")         
        return df
    

    ################################################################################################

    def analyse3_gpx(self):
                
        self.df_parcours['Cumul_Dist_m']=self.df_parcours['Delta_Dist_m'].cumsum()

        # Calculate cumulated time
        self.df_parcours['H_reel_s']=self.df_parcours['Delta_reel_s'].cumsum()
        # Convert time to hours:minutes:seconds
        self.df_parcours['Temps_course']=self.df_parcours['H_reel_s'].apply(lambda x: str(datetime.timedelta(seconds=x)))
        
        self.df_parcours['Cumul_D+_m']=self.df_parcours['Delta_D+_m'].cumsum()
        self.df_parcours['Cumul_D-_m']=self.df_parcours['Delta_D-_m'].cumsum()

        self.df_parcours['Delta_Dist_km'] = self.df_parcours['Delta_Dist_m']/1000
        self.df_parcours['Cumul_Dist_km'] = self.df_parcours['Cumul_Dist_m']/1000

    ################################################################################################

    def model_gpx(self):
        # Modélisation
        Y = self.df_parcours['Delta_reel_s']
        X = self.df_parcours[['Delta_Dist_m','Delta_D+_m','Cumul_Dist_m']]
        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.3, random_state=0)
        ridge_model = Ridge(alpha=1, fit_intercept=True)
        ridge_model.fit(X_train, y_train)
        print(f'{ridge_model.score(X_test, y_test)=}')

        print(f'{ridge_model.coef_=}')
        print(f'{ridge_model.intercept_=}')

        self.vit_plat = round(1/ridge_model.coef_[0]/1000*3600,2)
        self.vit_Dplus = int(1/ridge_model.coef_[1]*3600)
        self.ralentissement = round(ridge_model.coef_[2]*1000,2)
        self.fit_intercept = round(ridge_model.intercept_,2)

        # Prédiction

        self.df_parcours['Pred_T_Rom_s'] = ridge_model.predict(X)
        self.df_parcours['Pred_Cum_T_Rom_s'] = self.df_parcours['Pred_T_Rom_s'].cumsum()

    ################################################################################################
    
    def pred_temps(self, vit_plat,vit_Dplus,ralentissement,durée_stop,à_partir_de, fit_intercept):
        # print('Opti.: Vit_plat_km/h:',vit_plat,' | Vit_den+_m/h:', vit_Dplus,' | Ralent.:',ralentissement, ' | fit_intercept.:',fit_intercept)

        if self.modele_pred =='points_passages':
            df = self.df_ppassage
            df['Pred_Cum_T_Rom']=0 
            df['Pred_T_Rom']=0
            df['Pred_T_Rom']=round(df['Delta_Dist_km']/vit_plat+df['Delta_D+_m']/vit_Dplus+df['Cumul_Dist_km']*ralentissement/3600,2)+fit_intercept/3600
            # df['Heure_predite']=0 
            df['Pred_Cum_T_Rom'] = df['Pred_Cum_T_Rom'].astype(float)
            for i in range(1,len(df)):             
                df.loc[i,'Pred_Cum_T_Rom']=df.loc[i-1,'Pred_Cum_T_Rom']+df.loc[i,'Pred_T_Rom']
            for i in range(1,len(df)): 
                if df.loc[i,'Pred_Cum_T_Rom']>à_partir_de:
                    df.loc[i,'Pred_Cum_T_Rom']=df.loc[i,'Pred_Cum_T_Rom']+durée_stop
                df.loc[i,'Heure_predite']=(pd.to_datetime(f'{self.date} {self.heure_depart}')+pd.Timedelta(hours=(df.loc[i,'Pred_Cum_T_Rom']//1), minutes= (df.loc[i,'Pred_Cum_T_Rom']%1*60))).strftime("%a. %H:%M")         
                if df.loc[0,'H_reel_h_init']!='Not runned':
                    df.loc[i,'DELTA']=round(df.loc[i,'Pred_Cum_T_Rom']-df.loc[i,'H_reel_h_init'],2)
                    df['H_reel_h']=round(df['H_reel_h'],2)
                else:
                    df['DELTA']=0
            df.loc[0,'Heure_predite']=pd.to_datetime(f'{self.date} {self.heure_depart}').strftime("%a. %H:%M") 
            df.loc[0,'DELTA']=0.0

        elif self.modele_pred == 'gpx':
            df_parcours= self.df_parcours

            # self.vit_plat = round(1/model.get_params()['ridge'].coef_[0]/1000*3600,2)
            # self.vit_Dplus = int(1/model.get_params()['ridge'].coef_[1]*3600)
            # self.ralentissement = round(model.get_params()['ridge'].coef_[2]*1000,2)

            # ['Delta_Dist_m','Delta_D+_m','Cumul_Dist_m']


            df_parcours['Pred_T_Rom_s'] = round(df_parcours['Delta_Dist_m']*(3600/vit_plat/1000)+df_parcours['Delta_D+_m']*(3600/vit_Dplus)+df_parcours['Cumul_Dist_m']*ralentissement/1000,3) + fit_intercept
            df_parcours['Pred_Cum_T_Rom_s'] = df_parcours['Pred_T_Rom_s'].cumsum()
            df_parcours['Pred_T_Rom'] = df_parcours['Pred_T_Rom_s']/3600
            df_parcours['Pred_Cum_T_Rom'] = df_parcours['Pred_Cum_T_Rom_s']/3600


            df_ppassage = pd.DataFrame()
            target_distances = range(0,int(df_parcours['Cumul_Dist_km'].max()//1 + 2), 1)
            # Extract from df_parcours the rows which are the closed Dist_m from 1000, 2000,3000,4000,5000,6000,7000,8000,9000,10000
            closest_rows = []
            for target_distance in target_distances:
                closest_row = df_parcours.iloc[(df_parcours['Cumul_Dist_km'] - target_distance).abs().argsort()[:1],:].copy()
                closest_row['Point_passage'] = str(round(target_distance,0)) + 'km'
                closest_rows.append(closest_row)
            df = pd.DataFrame()
            df = pd.concat(closest_rows)

            df['Delta_Dist_km'] = df['Cumul_Dist_km'].diff()
            df['H_reel_h_init'] = df['H_reel_s']/3600
            df['H_reel_h'] = df['H_reel_h_init']
            df.reset_index(drop=True, inplace=True)
            df.loc[0, 'Delta_Dist_km'] = 0.0
            df.loc[0, 'Point_passage'] = 'Départ'
            df.loc[len(df)-1,'Point_passage'] = 'Arrivée'

            for i in range(1,len(df)): 
                if df.loc[i,'Pred_Cum_T_Rom']>à_partir_de:
                    df.loc[i,'Pred_Cum_T_Rom']=df.loc[i,'Pred_Cum_T_Rom']+durée_stop
                df.loc[i,'Heure_predite']=(pd.to_datetime(f'{self.date} {self.heure_depart}')+pd.Timedelta(hours=(df.loc[i,'Pred_Cum_T_Rom']//1), minutes= (df.loc[i,'Pred_Cum_T_Rom']%1*60))).strftime("%a. %H:%M")         
                if df.loc[0,'H_reel_h_init']!='Not runned':
                    x=df.loc[i,'Pred_Cum_T_Rom']-df.loc[i,'H_reel_h_init']
                    df.loc[i,'DELTA'] = f"{int(x):02}:{int((x -int(x))*60):02}:{int((x*3600)%60):02}"
                    df['H_reel_h']=round(df['H_reel_h'],2)
                else:
                    df['DELTA']=0
            df.loc[0,'Heure_predite']=pd.to_datetime(f'{self.date} {self.heure_depart}').strftime("%a. %H:%M") 
            df.loc[0,'DELTA']=0.0

        return df
    
    ################################################################################################

    def plot_parcours(self, df, vit_plat,vit_Dplus,ralentissement, fit_intercept):

        pts = [ (x,y) for x,y in zip(self.df_parcours['lat'],self.df_parcours['lon'])]

        map = folium.Map(location=[self.df_parcours['lat'].mean(), self.df_parcours['lon'].mean()], 
                         width = 1200, height = 600, 
                         zoom_start=11.25)
        
        folium.PolyLine(pts).add_to(map)

        geo_df_list = [ (x,y) for x,y in zip(df['lat'],df['lon'])]

        sw = self.df_parcours[['lat', 'lon']].min().values.tolist()
        ne = self.df_parcours[['lat', 'lon']].max().values.tolist()
        map.fit_bounds([sw, ne]) 

        

        for i, coordinates in enumerate(geo_df_list):

            try:
                HP = str(pd.to_datetime(df.loc[i,'Heure_Passage']).strftime("%a. %H:%M"))
            except:
                HP = df.loc[i,'Heure_Passage']

            txt = ''
            ic ='cloud'   
            couleur='blue'
            popContent = f''' {str(df.loc[i,'Point_passage'])}
                            <style>
                            table, th, td {{
                              border: 1px solid black;
                              border-collapse: collapse;
                              text-align: center; 
                                }}
                            </style> 
                            <table style="width:100%">
                              <tr>
                                <th>Distance:</th>
                                <th>Altitude:</th>
                                <th>D+:</th>
                              </tr>
                              <tr>
                               <td>{str(round(df.loc[i,'Cumul_Dist_km'],0))} km</td>
                               <td>{str(int(df.loc[i,'Altitude_m']))} m</td>
                               <td>{str(int(df.loc[i,'Cumul_D+_m']))} m</td>
                               </tr>
                               <tr>
                                <th>Heure Passage:</th>
                                <th>Heure Predite:</th>
                               </tr>
                               <tr>
                               <td>{HP}</td>
                               <td>{str((df.loc[i,'Heure_predite']))}</td>
                               </tr>
                               </table> '''
            iframe = folium.IFrame(popContent)
            popup1 = folium.Popup(iframe,
                                  min_width=350,
                                  max_width=400)   
            folium.Marker(location=coordinates,
                           popup = popup1,            
                           icon=plugins.BeautifyIcon(
                           icon="arrow-down", icon_shape="marker",
                           number=i,
                           )).add_to(map)
        #     folium.Marker(location=coordinates,
        #                    popup = popup1,            
        #                    icon=folium.Icon(color=couleur,icon=ic,prefix='fa')).add_to(map)
        titre = f'''
        <h2 align="center" style="font-size:16px font-family:Arial"><b>Trail {self.nom_id} </b></h2>
        <h4 align="center" style="font-size:16px font-family:Arial"> Modèle: Vitesse_plat:{vit_plat}km/h  Vitesse_D+:{vit_Dplus}m/h  Ralent.: {ralentissement}sec/km  fit_inter.: {fit_intercept}sec</h4>
        '''   

        map.get_root().html.add_child(folium.Element(titre))
        map.save(f'./data/pred/{self.nom_id}.html')
        display(map)    

        ################################################################################################

      