import tkinter as tk
import numpy as np

# constantes à utiliser dans le code
L, H = 600, 400  # dimensions de la fenêtre L = Largeur, H = Hauteur
R    = 10         # rayon de la balle
DT   = 0.05       # pas de temps
EPS  = 0.5        # seuil d'arrêt
BW   = 20         # largeur des bandes


# exception personnalisée
class ParametreInvalideError(Exception):
    pass


class ObjetPhysique:
    def __init__(self, position_x, position_y, vitesse_x, vitesse_y):
        self.position = np.array([position_x, position_y], dtype=float)
        self.vitesse  = np.array([vitesse_x, vitesse_y],   dtype=float)

    def vitesse_scalaire(self):
        return np.linalg.norm(self.vitesse)


# classe pour la balle
class Balle(ObjetPhysique):  # classe enfant qui hérite de la classe ObjetPhysique
    def __init__(self, position_x, position_y, vitesse_x, vitesse_y, mu):
        # appel de la classe exception pour lever les erreurs
        if not (0 <= position_x <= L) or not (0 <= position_y <= H):
            raise ParametreInvalideError("Les positions sont hors de la surface de la fenêtre.")
        if vitesse_x == 0 and vitesse_y == 0:
            raise ParametreInvalideError("La balle doit avoir une vitesse différente de zéro.")
        if not (0.0 <= mu <= 1.0):
            raise ParametreInvalideError("Le coefficient de friction doit être entre 0 et 1.")

        # appel du constructeur parent pour créer les attributs position et vitesse
        super().__init__(position_x, position_y, vitesse_x, vitesse_y)
        self.mu = mu  # coefficient de friction propre à la classe Balle

    def deplacer(self):
        # mise à jour de la vitesse de la balle en fonction de la friction (friction EN PREMIER)
        self.vitesse  *= (1 - self.mu * DT)   # la friction réduit la vitesse à chaque déplacement
        # mise à jour de la position de la balle en fonction de sa vitesse
        self.position += self.vitesse * DT

    def rebondir(self):  # rebondir sur les murs de la fenêtre
        # 4 if séparés (pas elif) pour gérer les coins — deux murs peuvent être touchés en même temps

        # côté gauche
        if self.position[0] <= R:
            self.position[0] = R  # éviter que la balle dépasse le mur
            n = np.array([1.0, 0.0])  # vecteur normal du mur
            self.vitesse = self.vitesse - 2 * np.dot(self.vitesse, n) * n  # nouvelle vitesse après rebond

        # côté droit
        if self.position[0] >= L - R:
            self.position[0] = L - R  # éviter que la balle dépasse le mur
            n = np.array([-1.0, 0.0])  # vecteur normal du mur
            self.vitesse = self.vitesse - 2 * np.dot(self.vitesse, n) * n  # nouvelle vitesse après rebond

        # côté du haut
        if self.position[1] <= R:
            self.position[1] = R  # éviter que la balle dépasse le mur
            n = np.array([0.0, 1.0])  # vecteur normal du mur
            self.vitesse = self.vitesse - 2 * np.dot(self.vitesse, n) * n  # nouvelle vitesse après rebond

        # côté du bas
        if self.position[1] >= H - R:
            self.position[1] = H - R  # éviter que la balle dépasse le mur
            n = np.array([0.0, -1.0])  # vecteur normal du mur
            self.vitesse = self.vitesse - 2 * np.dot(self.vitesse, n) * n  # nouvelle vitesse après rebond

    def calculer_trajectoire(self):  # méthode de Balle — pas une fonction flottante
        trajectoire = []  # liste afin de stocker les positions de la balle pour tracer la trajectoire
        while self.vitesse_scalaire() > EPS:  # tant que la vitesse de la balle est supérieure au seuil d'arrêt
            self.deplacer()   # déplacer la balle : friction + déplacement
            self.rebondir()   # faire rebondir la balle si elle touche les murs
            trajectoire.append(self.position.copy())  # ajouter la position actuelle à la trajectoire
        return trajectoire  # retourner la liste de la trajectoire — HORS du while


# Début de la classe Simulation afin de créer une interface pour la simulation de la balle avec tkinter
class Simulation:
    def __init__(self):
        self.root = tk.Tk()  # créer la fenêtre de l'interface
        self.root.title("Simulation de la balle")  # titre de la fenêtre
        self.trajectoire = []  # liste pour stocker les positions de la balle
        self.idx = 0  # index du pas courant dans l'animation
        self.creer_widgets()  # créer les widgets de l'interface
        self.root.mainloop()  # lancer la boucle principale

    def creer_widgets(self):  # méthode de la classe — PAS imbriquée dans __init__
        # panneau de contrôle à gauche pour les champs de saisie
        ctrl = tk.Frame(self.root, padx=10, pady=10)
        ctrl.pack(side=tk.LEFT, fill=tk.Y)

        # créer les champs de saisie pour les paramètres de la balle
        tk.Label(ctrl, text="Position X :").pack(anchor="w")
        self.position_x_entry = tk.Entry(ctrl, width=10)
        self.position_x_entry.insert(0, "100")  # valeur par défaut
        self.position_x_entry.pack(pady=(0, 4))

        tk.Label(ctrl, text="Position Y :").pack(anchor="w")
        self.position_y_entry = tk.Entry(ctrl, width=10)
        self.position_y_entry.insert(0, "100")  # valeur par défaut
        self.position_y_entry.pack(pady=(0, 4))

        tk.Label(ctrl, text="Vitesse X :").pack(anchor="w")
        self.vitesse_x_entry = tk.Entry(ctrl, width=10)
        self.vitesse_x_entry.insert(0, "300")  # valeur par défaut
        self.vitesse_x_entry.pack(pady=(0, 4))

        tk.Label(ctrl, text="Vitesse Y :").pack(anchor="w")
        self.vitesse_y_entry = tk.Entry(ctrl, width=10)
        self.vitesse_y_entry.insert(0, "200")  # valeur par défaut
        self.vitesse_y_entry.pack(pady=(0, 4))

        tk.Label(ctrl, text="Friction :").pack(anchor="w")
        self.friction_entry = tk.Entry(ctrl, width=10)
        self.friction_entry.insert(0, "0.5")  # valeur par défaut
        self.friction_entry.pack(pady=(0, 4))

        # créer le bouton pour lancer la simulation
        tk.Button(ctrl, text="Simuler", command=self.simuler).pack(fill=tk.X, pady=(8, 2))

        # labels d'information
        tk.Label(ctrl, text="-" * 20).pack(pady=(6, 4))
        self.lbl_final  = tk.Label(ctrl, text="--", font=("Courier", 9), justify="left")
        self.lbl_final.pack()
        self.lbl_erreur = tk.Label(ctrl, text="", font=("Courier", 9), fg="red", justify="left")
        self.lbl_erreur.pack(pady=(4, 0))

        # canevas à droite : bandes brunes + tapis vert
        self.canvas = tk.Canvas(self.root, width=L + 2*BW, height=H + 2*BW, bg="#111")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        self.canvas.create_rectangle(0,  0,  L+2*BW, H+2*BW, fill="#6b3e1e", outline="")  # bandes
        self.canvas.create_rectangle(BW, BW, BW+L,   BW+H,   fill="#1a5c2a", outline="")  # tapis
        self.canvas.create_rectangle(BW, BW, BW+L,   BW+H,   fill="", outline="#c8a465", width=2)
        self.balle_dessin = self.canvas.create_oval(0, 0, 0, 0, fill="white", outline="red", width=2)

    def simuler(self):  # méthode de la classe — PAS imbriquée dans creer_widgets
        self.lbl_erreur.config(text="")  # effacer l'erreur précédente
        try:
            # récupérer les valeurs des paramètres à partir des champs de saisie
            position_x = float(self.position_x_entry.get())
            position_y = float(self.position_y_entry.get())
            vitesse_x  = float(self.vitesse_x_entry.get())
            vitesse_y  = float(self.vitesse_y_entry.get())
            friction   = float(self.friction_entry.get())

            # créer une instance de la classe Balle avec les paramètres récupérés
            balle = Balle(position_x, position_y, vitesse_x, vitesse_y, friction)

            # calculer la trajectoire de la balle
            self.trajectoire = balle.calculer_trajectoire()

            # afficher la position finale
            p_fin = self.trajectoire[-1]
            self.lbl_final.config(text=f"Position finale : ({p_fin[0]:.1f}, {p_fin[1]:.1f})")

            # démarrer l'animation depuis le début
            self.idx = 0
            self.animer()

        except ParametreInvalideError as e:  # gérer les exceptions personnalisées
            self.lbl_erreur.config(text=str(e))
        except ValueError:
            self.lbl_erreur.config(text="Les champs doivent être des nombres.")

    def animer(self):  # méthode de la classe — PAS imbriquée dans simuler
        # arrêter quand on a affiché tous les pas
        if self.idx >= len(self.trajectoire):
            return

        # récupérer la position du pas courant
        position_x, position_y = self.trajectoire[self.idx]
        cx, cy = position_x + BW, position_y + BW  # décalage pour les bandes visuelles

        # déplacer l'ovale sur le canevas
        self.canvas.coords(self.balle_dessin, cx-R, cy-R, cx+R, cy+R)

        self.idx += 1 # passer au pas suivant index pour la prochain=e animationgi
        self.root.after(30, self.animer)  # rappeler animer dans 30ms


# point d'entrée pour lancer la simulation
if __name__ == "__main__":
    Simulation()  # créer une instance de la classe Simulation pour lancer l'interface
