import tkinter as tk
import numpy as np

# constantes à utiliser dans le code

L, H = 600,400 # dimensions de la fenêtre L = Largeur, H = Hauteur
R = 10 # rayon de la balle
DT = 0.05 # pas de temps
EPS = 0.5 #seuil d'arrêt 
BW = 20 # largeur des bandes

# exception personnalisée
class ParametreInvalideError(Exception):
    pass

class ObjetPhysique:
    def __init__(self,position_x, position_y, vitesse_x, vitesse_y):
        self.position = np.array([position_x, position_y])
        self.vitesse = np.array([vitesse_x, vitesse_y])

    def vitesse_scalaire(self):
        return np.linalg.norm(self.vitesse)
    
# classe pour la balle
class Balle(ObjetPhysique ): # classe enfant qui hérite de la classe ObjetPhysique 
    def __init__(self,position_x ,position_y,vitesse_x,vitesse_y,mu): # ajoute de mu (friction) 
             # appel de la classe exception pour lever les erreurs
             if not (0 <= position_x <= L) or not (0 <= position_y <= H):
                  raise ParametreInvalideError("Les positions sont hors de la surface de la fenêtre.")
             if vitesse_x == 0 and vitesse_y == 0:
                  raise ParametreInvalideError("La balle doit avoir une vitesse différente de zéro.") 
             if not (0.0 <= mu <= 1.0):
                  raise ParametreInvalideError("Le coefficient de friction doit être entre 1 et 0.") 
             
             # appel du constructeur parent pour créér plus d'attributs position et vitesse
             super().__init__(position_x,position_y,vitesse_x,vitesse_y)
             self.mu = mu # coefficient de friction qui est propre à la classe balle seulement
    
    def deplacer(self): 
        # mise à jour de la position de la balle en fonction de sa vitesse 
        self.position += self.vitesse * DT
        # mise à jour de la vitesse de la balle en fonction de la friction 
        self.vitesse *= (1 - self.mu) # la friction réduisant la vitesse de la balle à chaque déplacement 

    def rebondir(self): # rebondir sur les murs de la fenêtre 
         # côté gauche 
        if self.position[0] <= R:
              self.position[0] = R # éviter que la balle dépasse le mur
              n = np.array([1,0,0.0]) # vecteur normal du mur
        self.vitesse = self.vitesse - 2 * np.dot(self.vitesse, n) * n # calcul de la nouvelle vitesse après le rebond
        # côté droit 
        if self.position[0] >= L - R:
             self.position[0] = L - R # éviter que la balle dépasse le mur
             n = np.array([-1,0,0.0]) # vecteur normal du mur
             self.vitesse = self.vitesse - 2 * np.dot(self.vitesse, n) * n # calcul de la nouvelle vitesse après le rebond
             # côté du haut 