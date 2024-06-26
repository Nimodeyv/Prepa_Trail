import folium
import folium.plugins as plugins
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
# import ipywidgets as widgets
# from IPython.display import display
import seaborn as sns
from datetime import datetime, timedelta
import streamlit as st
from streamlit_folium import st_folium, folium_static


from dep.coureur import Coureur
from dep.trails import Trail
from dep.utils_trails import pred, plot_data


def main():

    Pugin = Coureur(nom= 'PUGIN',
                   prenom= 'Jean-Francois',
                   poids=65,
                   conso_eau = 0.5, # l/h
                   conso_glucide = 60, # g/h
                   ) 
    
    coureur_choisi = Pugin

    PIK = f"./data/coureurs/{coureur_choisi.prenom_nom}.dat"
    Trails_objects = []
    with open(PIK, "rb") as f:
        while True:
            try:
                Trails_objects.append(pickle.load(f))
            except EOFError:
                break

    with st.sidebar:
            st.title('Prepare ton trail !')
                
            # selected_coureur = st.selectbox("Select a runner", file_list)

            selected_trail = st.selectbox("Select a trail", [T.nom_id for T in Trails_objects[:-2]], 
                                          #on_change=handle_selectbox_change,
                                          )

            vitesse_plat = st.slider("Vitesse plat (km/h):", min_value=5.0, max_value=20.0, value=13.0, step=0.1)
            vitesse_Dplus = st.slider("Vitesse Dénivélé+ (m/h):", min_value=600, max_value=6000, value=1713, step=25)
            Ralentissement = st.slider("Ralentissement (sec/km):", min_value=-20.0, max_value=10.0, value=5.1, step=0.5)
            fit_intercept =  0 #st.slider("fit_intercept:", min_value=0.0, max_value=10.0, value=0.0, step=0.01)

            

    # get index within Trails_objects of selected trail
    i = [T.nom_id for T in Trails_objects[:-2]].index(selected_trail)   
    T = Trails_objects[i]

        
    with st.sidebar:
        ravito = [] 
        for i in range(len(T.df_ppassage)-1):
            checkbox_label = st.checkbox(T.df_ppassage.loc[i+1, 'Point_passage'], 
                                         key=f'checkbox_{i+1}')
            if checkbox_label:
                ravito.append(T.df_ppassage.loc[i+1,'Point_passage'])


    with st.sidebar:
        button_clicked = st.button("Prediction")

        st.image('./data/logo/logo_transparent.png', width = 100 )

        
    if button_clicked:


        df_p, df_eau, df_glucide = pred(T=T, i=i, vit_plat=vitesse_plat, vit_Dplus=vitesse_Dplus, ralentissement=Ralentissement, fit_intercept=fit_intercept,
         conso_eau=coureur_choisi.conso_eau, liste_ravito_liquide=ravito, 
         conso_glucide=coureur_choisi.conso_glucide, liste_ravito_solide=ravito,
         )
        
        st.write(f"Prédiction pour {coureur_choisi.prenom_nom} sur le trail {T.nom_id}")

        # Display map in the main window
        map = T.plot_parcours(df=df_p, vit_plat=vitesse_plat, vit_Dplus=vitesse_Dplus, 
                        ralentissement=Ralentissement, fit_intercept=fit_intercept)
        
        folium_static(map, width=1000)
        
        
        # Display the plots in the main window
        fig = plot_data(T=T, i=i, df= df_p, axeX='Cumul_Dist_km', axeY1='H_reel_h', axeY2='Pred_Cum_T_Rom', 
                  df_eau=df_eau, df_glucide=df_glucide, conso_eau=coureur_choisi.conso_eau, conso_glucide=coureur_choisi.conso_glucide,
                  vit_plat=vitesse_plat, vit_Dplus=vitesse_Dplus, ralentissement=Ralentissement, fit_intercept=fit_intercept,
                  )
        
        st.pyplot(fig, use_container_width=False)
        # st.image(f'./data/pred/{T.nom_id}_{vitesse_plat}_{vitesse_Dplus}_{round(Ralentissement,3)}_{fit_intercept}.png', width=1000)
        
    
        # Merge column "Eau_à_emporter" of df_eau with df_p on 'Point_passage'
        df_p = df_p.merge(df_eau[['Point_passage', 'Cumul_Dist_km', 'Eau_à_emporter']], on=['Point_passage','Cumul_Dist_km'], how='left')
        df_p = df_p.merge(df_glucide[['Point_passage', 'Cumul_Dist_km', 'Glucides_à_emporter']], on=['Point_passage', 'Cumul_Dist_km'], how='left')


        st.dataframe(df_p[['Point_passage', 'Cumul_Dist_km','Cumul_D+_m','Pred_Cum_T_Rom',
                    'Heure_predite', 'Eau_à_emporter', 'Glucides_à_emporter']], 
                    use_container_width=False, #width=1000, height=900,
                    )

        

if __name__=="__main__":
    main()