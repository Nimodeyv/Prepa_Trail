class Coureur:
    def __init__(self, nom, prenom, poids, conso_eau=0.5, conso_glucide=60):
        self.nom = nom.upper()
        self.prenom = prenom
        self.poids = poids # kg
        self.conso_eau = conso_eau # l/h
        self.conso_glucide = conso_glucide # g/h

        self.prenom_nom = prenom + " " + self.nom