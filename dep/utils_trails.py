import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from IPython.display import display



################################################################################################


def plot_data(T, i, df,axeX, axeY1, axeY2, df_eau, df_glucide,  conso_eau, conso_glucide, 
              vit_plat,vit_Dplus,ralentissement, fit_intercept):

            fig, ax = plt.subplots(4,1, figsize=(15,12))
            T.df_parcours['Altitude_m'] = T.df_parcours['Altitude_m'].astype(float)
            T.df_parcours[axeX] = T.df_parcours[axeX].astype(float)
            sns.lineplot(data=T.df_parcours, x=axeX, y='Altitude_m', ax=ax[0], color='black')
            ax[0].fill_between(T.df_parcours[axeX], T.df_parcours['Altitude_m'], color="skyblue", alpha=0.4)
            sns.scatterplot(data=df, x=axeX, y='Altitude_m', ax=ax[0], color='red')
            # Put labels on scatterplot from df colum 'Point_passage'
            for j, txt in enumerate(df['Point_passage']):
                ax[0].annotate(txt, (df[axeX].iloc[j], df['Altitude_m'].iloc[j]), fontsize=8)
            ax[0].set_xlabel('')
            ax[0].set_ylabel('Altitude (m)')
            ax[0].grid()

            sns.scatterplot(data=df_eau, x='Cumul_Dist_km', y='Eau_à_emporter', ax=ax[1], color='red')
            for j in range(len(df_eau)-1):
                ax[1].plot([df_eau.loc[j,'Cumul_Dist_km'],df_eau.loc[j,'Cumul_Dist_km']],
                        [0,df_eau.loc[j,'Eau_à_emporter']], color='blue')
                ax[1].plot([df_eau.loc[j,'Cumul_Dist_km'],df_eau.loc[j+1,'Cumul_Dist_km']],
                        [df_eau.loc[j,'Eau_à_emporter'],0], color='blue')
                ax[1].annotate(f"{df_eau.loc[j,'Eau_à_emporter']} lit", (df_eau.loc[j,'Cumul_Dist_km']+1,
                                                                        df_eau.loc[j,'Eau_à_emporter']), fontsize=11)
                ax[1].fill_between([df_eau.loc[j,'Cumul_Dist_km'],df_eau.loc[j+1,'Cumul_Dist_km']],
                                [df_eau.loc[j,'Eau_à_emporter'],0], color="skyblue", alpha=0.4)
            ax[1].text(0, 0.1, f'Conso. eau:{conso_eau} l/h')
            ax[0].set_xlabel('')
            ax[1].grid()


            sns.scatterplot(data=df_glucide, x='Cumul_Dist_km', y='Glucides_à_emporter', ax=ax[2], color='brown')
            for j in range(len(df_glucide)-1):
                ax[2].plot([df_glucide.loc[j,'Cumul_Dist_km'],df_glucide.loc[j,'Cumul_Dist_km']],
                        [0,df_glucide.loc[j,'Glucides_à_emporter']], color='black')
                ax[2].plot([df_glucide.loc[j,'Cumul_Dist_km'],df_glucide.loc[j+1,'Cumul_Dist_km']],
                        [df_glucide.loc[j,'Glucides_à_emporter'],0], color='black')
                ax[2].annotate(f"{int(df_glucide.loc[j,'Glucides_à_emporter'])}g", 
                            (df_glucide.loc[j,'Cumul_Dist_km']+1,df_glucide.loc[j,'Glucides_à_emporter']), fontsize=11)
                ax[2].fill_between([df_glucide.loc[j,'Cumul_Dist_km'],df_glucide.loc[j+1,'Cumul_Dist_km']],
                                [df_glucide.loc[j,'Glucides_à_emporter'],0], color="pink", alpha=0.4)
            ax[2].text(0, 5, f'Conso. glucides:{conso_glucide} g/h')
            ax[0].set_xlabel('')
            ax[2].grid()



            sns.lineplot(data=df, x=axeX, y=axeY1, ax=ax[3], label="Real time", color='blue')
            sns.lineplot(data=df, x=axeX, y=axeY2, ax=ax[3], label="Predicted time", color='red')
            sns.scatterplot(data=df, x=axeX, y=axeY2, ax=ax[3], label="Predicted time", color='red')
            for j in range(len(df)):
                ax[3].text(df.loc[j,axeX],df.loc[j,axeY2],f'{round(df.loc[j,axeY2],1)}h', color='blue', 
                        verticalalignment='bottom', horizontalalignment='right', fontsize=10)
            ax[3].set_ylabel('Cumulated time (s)')
            ax[0].set_xlabel('')
            ax[3].legend()
            ax[3].grid()

            plt.show()

            # fig.savefig(f'./data/pred/{T.nom_id}_{vit_plat}_{vit_Dplus}_{round(ralentissement,3)}_{fit_intercept}.png')

            return fig

################################################################################################

def add_table_to_map(T, i,vit_plat,vit_Dplus,ralentissement, fit_intercept, coureur):

    message_start = f"""
          <head>
          <meta http-equiv="Content-Type" content="text/html; charset=latin-1">
          <title>Trail de {coureur}</title>"""
    message_style = """
            <style type="text/css" media="screen">
                #customers {
                font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
                font-size: 14px;
                border-collapse: collapse;
                width: 100%;
                }
                #customers td, #customers th {
                border: 1px solid #ddd;
                padding: 8px;
                }
                #customers tr:nth-child(even){background-color: #f2f2f2;}
                #customers tr:hover {background-color: #ddd;}
                #customers th {
                padding-top: 12px;
                padding-bottom: 12px;
                text-align: left;
                background-color: #003d77;
                color: white;
                }
            </style>
            </head>
            <body>
        """

    with open(f'./data/pred/{T.nom_id}.html', 'r') as f:
            data = f.read()

    df_p, _, _ = pred(i, vit_plat,vit_Dplus,ralentissement, fit_intercept)

    titre = f'''
        <h3 align="center" style="font-size:16px font-family:Arial"><b></b></h3>
        '''
    fig = f'<img src="{T.nom_id}_{vit_plat}_{vit_Dplus}_{round(ralentissement,3)}_{fit_intercept}.png" alt="Trails" width="1000" height="900">'
    message_body = df_p[['Point_passage', 'Cumul_Dist_km','Cumul_D+_m','Temps_course','H_reel_h',
                         'Pred_Cum_T_Rom','Heure_Passage','Heure_predite','DELTA']].to_html(index=False, table_id="customers")
    data = message_start + message_style + titre + data + fig + message_body
    with open(f'./data/pred/{T.nom_id}_{vit_plat}_{vit_Dplus}_{round(ralentissement,3)}_{fit_intercept}.html', 'w') as f:
        f.write(data)


################################################################################################

    
def pred(T, i,vit_plat, vit_Dplus, ralentissement, fit_intercept, 
         conso_eau, liste_ravito_liquide, conso_glucide, liste_ravito_solide,
         durée_arret = 0, à_partir_de = 13):
        
        df_p = T.pred_temps(vit_plat,vit_Dplus,ralentissement,durée_arret,à_partir_de, fit_intercept)

        parcours_plot(T, i, df_p, vit_plat, vit_Dplus, ralentissement, fit_intercept)

        df_eau, df_glucide =  calc_ravito(i, df_p, conso_eau, liste_ravito_liquide, conso_glucide, liste_ravito_solide)
        # display(df_eau)

        plot_data(T=T, i=i, df= df_p, axeX='Cumul_Dist_km', axeY1='H_reel_h', axeY2='Pred_Cum_T_Rom', 
                  df_eau=df_eau, df_glucide=df_glucide, conso_eau=conso_eau, conso_glucide=conso_glucide,
                  vit_plat=vit_plat, vit_Dplus=vit_Dplus, ralentissement=ralentissement, fit_intercept=fit_intercept,
                  )

        # Convert column format
        df_p['Delta_Dist_km'] = round(df_p['Delta_Dist_km'],1)
        df_p['Cumul_D+_m'] = df_p['Cumul_D+_m'].apply(int)
        df_p['Cumul_Dist_km'] = round(df_p['Cumul_Dist_km'],2)
        df_p['Pred_Cum_T_Rom'] = round(df_p['Pred_Cum_T_Rom'],2)
        try:
            df_p['Heure_Passage'] = df_p['Heure_Passage'].apply(lambda x: pd.to_datetime(x).strftime("%a. %H:%M"))
        except:
            pass
        display(df_p[['Point_passage', 'Cumul_Dist_km','Cumul_D+_m','Temps_course','H_reel_h','Pred_Cum_T_Rom',
                    'Heure_Passage','Heure_predite','DELTA']])
        # add_table_to_map(i,vit_plat,vit_Dplus,ralentissement)
        return df_p, df_eau, df_glucide

################################################################################################

def parcours_plot(T, i, df_p, vit_plat, vit_Dplus, ralentissement, fit_intercept):
       T.plot_parcours(df_p, vit_plat, vit_Dplus, ralentissement, fit_intercept)  

################################################################################################


def calc_ravito(i, df_p, conso_eau, liste_ravito_liquide, conso_glucide, liste_ravito_solide):
        
        df_p['Ravito_liquide'] = 0
        df_p['Ravito_solide']=0
        df_p.loc[df_p['Point_passage'].isin(liste_ravito_liquide), 'Ravito_liquide'] = 1
        df_p.loc[df_p['Point_passage'].isin(liste_ravito_solide), 'Ravito_solide'] = 1

        df_eau = df_p.loc[df_p['Ravito_liquide']==1, ['Point_passage', 'Cumul_Dist_km', 'Pred_Cum_T_Rom', 
                                                'Ravito_liquide']]
        df_glucide = df_p.loc[df_p['Ravito_solide']==1, ['Point_passage', 'Cumul_Dist_km', 'Pred_Cum_T_Rom', 
                                                'Ravito_solide']]


        df_eau.reset_index(drop=True, inplace=True)
        df_glucide.reset_index(drop=True, inplace=True)
        df_eau['DT'] = df_eau['Pred_Cum_T_Rom'].diff()
        df_glucide['DT'] = df_glucide['Pred_Cum_T_Rom'].diff()
        df_eau['DT'] = df_eau['DT'].fillna(0)
        df_glucide['DT'] = df_glucide['DT'].fillna(0)

        for i in range(len(df_eau)-1):
            df_eau.loc[i,'Eau_à_emporter'] = round(df_eau.loc[i+1,'DT']*conso_eau,1)
        for i in range(len(df_glucide)-1):  
            df_glucide.loc[i,'Glucides_à_emporter'] = round(df_glucide.loc[i+1,'DT']*conso_glucide,1)

        return df_eau, df_glucide

################################################################################################
