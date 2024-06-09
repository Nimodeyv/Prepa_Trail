### class trail

       .nom_id            Nom du trail
       .date              Date du trail
       .suivi             Site pour suivre le trail livetrail ou livetrack, gpx si prédiction à partir de gpx
       .heure_depart      Heure de départ du trail
       .csv_file          Nom du fichier avec les points de passage
       .df_ppassage       DataFrame avec les points de passage + les prédictions
       .df_parcours       DataFrame du parcours après chargement du fichier gpx
       .vit_plat          Paramètre  1 de correlation après correlation linéaire en km/h
       .vit_Dplus         Paramètre  2 de correlation après correlation linéaire en m/h
       .ralentissement    Paramètre  3 de correlation après correlation linéaire en sec/km
       .fit_interecept    Paramètre  4 qui correspond à l'offset (ordonnée à l'origine) en sec
       .modele_pred       Modèle de prédiction à partir des points de passage ou gpx

ATTENTION : Il faut que le nom du trail soit le meme que celui dans la recherche Livetrail sinon il ne va pas le trouver

### df_ppassage : Dataframe des points de passage du trail

INPUT

<pre>
- Point_passage         Etape de passage  
- Altitude              Altitude en m
- Cumul_Dist_km         Distance cumulée en km (input donné, non calculé du gpx)
- Delta_Dist_km         Distance en km entre la point précédent et ce point de passage
- Cumul_D+_m            Dénivelé positif cumulé en m (input donné, non calculé du gpx)
- Delta_D+_m            Dénivelé positif entre le point précédent et ce point de passage
- lon                   Longitude de ce point de passage au format décimal
- lat                   Latitude de ce point de passage au format décimal
- Heure_Passage         Heure de passage à ce point au format DAY.HH:MM
- Temps_course          Temps de course à ce point de passage au format HH:MM:SS
- Classement            Classement à ce point de passage
- Vitesse_km/h          Vitesse en km/h à ce point de passage depuis le début du parcours
- H_reel_h              Heure de passage à ce point au format décimal en heure
- Delta_reel_h          Temps entre le précédent point et ce point de passage au format décimal en heure
- (Services)              Services disponibles à ce point de passage (liste pouvant contenir les services ci-dessous)
                            - BUS DE L'ORGANISATION
                            - SECOURS
                            - WC
                            - SAC D'ALLEGEMENT
                            - RAVITALLEMENT LIQUIDE
                            - RAVITAILLEMENT SOLIDE
                            - PRODUITS NÄAK
</pre>

CALCUL

<pre>
- H_reel_h_init         Heure de passage à ce point au format décimal en heure (sans les points de passage manquant s'il y en a)
- Delta_reel_h_init     Temps entre le précédent point et ce point de passage au format décimal en heure (sans les points manquants)
- Trail                 Nom du trail
- Pred_Cum_T_Rom        Temps prédit cumulé au format décimal en heure
- Pred_T_Rom            Temps prédit entre le précédent point et ce point de passage au format décimal en heure
- Heure_predite         Heure prédite de passage au format DAY.HH:MM
- DELTA                 Delta entre heure de passage réelle et heure prédite au format décimal en heure
</pre>

### df_parcours: Dataframe du fichier gpx du trail

INPUT

<pre>
- Altitude_m            Altitude en m
- Heure_Passage         Heure à ce point du parcours au format YYYY-MM-DD HH:MM:SS+00:00
- hr
- cad
- lon                   Longitude de ce point de parcours au format décimal
- lat                   Latitude de ce point de parcours au format décimal
- Delta_Dist_m          Distance en m entre la point précédent et ce point de parcours calculé par géodesic
- Delta_reel_s          Temps entre le précédent point et ce point de parcours au format décimal en sécondes
- Dénivelé_m            Dénivelé entre le point précédent et ce point de parcours en m
- Delta_D+_m            Dénivelé postif entre le point précédent et ce point de parcours en m
- Delta_D-_m            Dénivelé négatif entre le point précédent et ce point de parcours en m
- Cumul_Dist_m          Distance cumulée en m (calculé à partir du gpx)
- H_reel_s              Temps de course à ce point de parcours au format décimal en secondes
- Temps_course          Temps de course à ce point de parcours au format HH:MM:SS
- Cumul_D+_m            Dénivelé positif cumulé en m (calculé à partir du gpx)
- Cumul_D-_m            Dénivelé négatif cumulé en m (calculé à partir du gpx)
- Delta_Dist_km         Distance en km entre la point précédent et ce point de parcours calculé par géodesic
- Cumul_Dist_km         Distance cumulée en km (calculé à partir du gpx)
</pre>
