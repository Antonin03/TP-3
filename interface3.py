import tkinter as tk
from tkinter import filedialog
import numpy as np
import json

# constantes par défaut (seront remplacées par le fichier de configuration)
L, H = 600, 400  # dimensions de la fenêtre L = Largeur, H = Hauteur
R    = 10         # rayon de la balle
DT   = 0.05       # pas de temps
EPS  = 0.5        # seuil d'arrêt
BW   = 20         # largeur des bandes


# exceptions personnalisées — une par type d'erreur pour des messages clairs
class ParametreInvalideError(Exception):
    pass

class FichierIntrouvableError(Exception):
    pass

class FichierMalformeError(Exception):
    pass

class ChampManquantError(Exception):
    pass


# fonction pour lire et valider le fichier de configuration
def lire_config(chemin):
    # 1. essayer d'ouvrir le fichier
    try:
        with open(chemin, "r") as f:
            config = json.load(f)  # convertit le JSON en dictionnaire Python
    except FileNotFoundError:
        raise FichierIntrouvableError(f"Le fichier '{chemin}' est introuvable.")
    except json.JSONDecodeError:
        raise FichierMalformeError("Le fichier n'est pas un JSON valide.")

    # 2. vérifier que tous les champs obligatoires sont présents
    champs_obligatoires = ["L", "H", "mu", "rayon", "balles"]
    for champ in champs_obligatoires:
        if champ not in config:
            raise ChampManquantError(f"Le champ '{champ}' est manquant dans le fichier.")

    # 3. valider les valeurs
    if config["L"] <= 0 or config["H"] <= 0:
        raise ParametreInvalideError("Les dimensions L et H doivent être positives.")
    if not (0.0 <= config["mu"] <= 1.0):
        raise ParametreInvalideError("La friction mu doit être entre 0 et 1.")
    if config["rayon"] <= 0:
        raise ParametreInvalideError("Le rayon doit être positif.")
    if not isinstance(config["balles"], list) or len(config["balles"]) == 0:
        raise ParametreInvalideError("Le fichier doit contenir au moins une balle.")

    # 4. valider chaque balle dans la liste
    for i, balle in enumerate(config["balles"]):
        for champ in ["position_x", "position_y", "vitesse_x", "vitesse_y"]:
            if champ not in balle:
                raise ChampManquantError(f"Balle {i+1} : le champ '{champ}' est manquant.")

    return config  # retourner le dictionnaire validé


class ObjetPhysique:
    def __init__(self, position_x, position_y, vitesse_x, vitesse_y):
        self.position = np.array([position_x, position_y], dtype=float)
        self.vitesse  = np.array([vitesse_x, vitesse_y],   dtype=float)

    def vitesse_scalaire(self):
        return np.linalg.norm(self.vitesse)


# classe pour la balle — maintenant elle reçoit L, H, R depuis le fichier
class Balle(ObjetPhysique):  # classe enfant qui hérite de la classe ObjetPhysique
    def __init__(self, position_x, position_y, vitesse_x, vitesse_y, mu, L, H, R):
        # appel de la classe exception pour lever les erreurs
        if not (0 <= position_x <= L) or not (0 <= position_y <= H):
            raise ParametreInvalideError("Les positions sont hors de la surface de la fenêtre.")
        if vitesse_x == 0 and vitesse_y == 0:
            raise ParametreInvalideError("La balle doit avoir une vitesse différente de zéro.")

        # appel du constructeur parent pour créer les attributs position et vitesse
        super().__init__(position_x, position_y, vitesse_x, vitesse_y)
        self.mu = mu  # coefficient de friction propre à la classe Balle
        self.L  = L   # dimensions lues depuis le fichier
        self.H  = H
        self.R  = R

    def rebondir(self):  # rebondir sur les murs de la fenêtre
        # 4 if séparés (pas elif) pour gérer les coins

        # côté gauche
        if self.position[0] <= self.R:
            self.position[0] = self.R
            n = np.array([1.0, 0.0])
            self.vitesse = self.vitesse - 2 * np.dot(self.vitesse, n) * n

        # côté droit
        if self.position[0] >= self.L - self.R:
            self.position[0] = self.L - self.R
            n = np.array([-1.0, 0.0])
            self.vitesse = self.vitesse - 2 * np.dot(self.vitesse, n) * n

        # côté du haut
        if self.position[1] <= self.R:
            self.position[1] = self.R
            n = np.array([0.0, 1.0])
            self.vitesse = self.vitesse - 2 * np.dot(self.vitesse, n) * n

        # côté du bas
        if self.position[1] >= self.H - self.R:
            self.position[1] = self.H - self.R
            n = np.array([0.0, -1.0])
            self.vitesse = self.vitesse - 2 * np.dot(self.vitesse, n) * n

    def calculer_trajectoire(self):
        trajectoire = []  # liste pour stocker les positions de la balle
        while self.vitesse_scalaire() > EPS:  # tant que la balle bouge
            self.vitesse  *= (1 - self.mu * DT)   # 1. friction
            self.rebondir()                        # 2. rebonds sur les murs
            self.position += self.vitesse * DT    # 3. déplacement
            trajectoire.append(self.position.copy())  # sauvegarder la position
        return trajectoire  # retourner la trajectoire — HORS du while


# classe pour gérer l'interface graphique
class Simulation:
    def __init__(self):
        self.root = tk.Tk()  # créer la fenêtre de l'interface
        self.root.title("Simulation de la balle")  # titre de la fenêtre
        self.trajectoire = []  # liste pour stocker les positions de la balle
        self.idx  = 0          # index du pas courant dans l'animation
        self.config = None     # configuration lue depuis le fichier
        self.creer_widgets()   # créer les widgets de l'interface
        self.root.mainloop()   # lancer la boucle principale

    def creer_widgets(self):
        # panneau de contrôle à gauche
        ctrl = tk.Frame(self.root, padx=10, pady=10)
        ctrl.pack(side=tk.LEFT, fill=tk.Y)

        # section chargement du fichier de configuration
        tk.Label(ctrl, text="Fichier de configuration :").pack(anchor="w")
        tk.Button(ctrl, text="Choisir un fichier...", command=self.choisir_fichier).pack(fill=tk.X, pady=(0, 4))
        self.lbl_fichier = tk.Label(ctrl, text="Aucun fichier choisi", font=("Courier", 8), fg="grey", wraplength=180)
        self.lbl_fichier.pack(anchor="w")

        tk.Label(ctrl, text="-" * 20).pack(pady=(8, 4))

        # bouton pour lancer la simulation
        tk.Button(ctrl, text="Simuler", command=self.simuler).pack(fill=tk.X, pady=(0, 4))

        # labels d'information
        tk.Label(ctrl, text="-" * 20).pack(pady=(6, 4))
        self.lbl_config = tk.Label(ctrl, text="--", font=("Courier", 9), justify="left")
        self.lbl_config.pack()
        self.lbl_final  = tk.Label(ctrl, text="--", font=("Courier", 9), justify="left")
        self.lbl_final.pack(pady=(4, 0))
        self.lbl_erreur = tk.Label(ctrl, text="", font=("Courier", 9), fg="red", justify="left", wraplength=180)
        self.lbl_erreur.pack(pady=(4, 0))

        # canevas à droite — sera redessiné quand le fichier est chargé
        self.canvas = tk.Canvas(self.root, width=L + 2*BW, height=H + 2*BW, bg="#111")
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        self._dessiner_table(L, H)  # dessiner avec les dimensions par défaut

    def _dessiner_table(self, largeur, hauteur):
        # effacer et redessiner la table avec les nouvelles dimensions
        self.canvas.config(width=largeur + 2*BW, height=hauteur + 2*BW)
        self.canvas.delete("all")  # effacer tout
        self.canvas.create_rectangle(0,  0,  largeur+2*BW, hauteur+2*BW, fill="#6b3e1e", outline="")  # bandes
        self.canvas.create_rectangle(BW, BW, BW+largeur,   BW+hauteur,   fill="#1a5c2a", outline="")  # tapis
        self.canvas.create_rectangle(BW, BW, BW+largeur,   BW+hauteur,   fill="", outline="#c8a465", width=2)
        self.balle_dessin = self.canvas.create_oval(0, 0, 0, 0, fill="white", outline="red", width=2)

    def choisir_fichier(self):
        # ouvrir la fenêtre de sélection de fichier — demandé par l'énoncé
        chemin = filedialog.askopenfilename(
            title="Choisir un fichier de configuration",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        if not chemin:
            return  # l'utilisateur a annulé

        self.lbl_erreur.config(text="")  # effacer l'erreur précédente
        try:
            self.config = lire_config(chemin)  # lire et valider le fichier

            # afficher le nom du fichier et la configuration lue
            self.lbl_fichier.config(text=chemin, fg="green")
            self.lbl_config.config(
                text=f"L={self.config['L']}  H={self.config['H']}\n"
                     f"mu={self.config['mu']}  R={self.config['rayon']}\n"
                     f"{len(self.config['balles'])} balle(s) trouvée(s)"
            )

            # redessiner la table avec les nouvelles dimensions
            self._dessiner_table(self.config["L"], self.config["H"])

        except (FichierIntrouvableError, FichierMalformeError,
                ChampManquantError, ParametreInvalideError) as e:
            self.lbl_erreur.config(text=str(e))
            self.lbl_fichier.config(fg="red")

    def simuler(self):
        self.lbl_erreur.config(text="")  # effacer l'erreur précédente

        # vérifier qu'un fichier a été chargé
        if self.config is None:
            self.lbl_erreur.config(text="Veuillez d'abord choisir un fichier de configuration.")
            return

        try:
            # lire les paramètres depuis la config — plus depuis des champs Entry
            mu = self.config["mu"]
            lf = self.config["L"]
            hf = self.config["H"]
            rf = self.config["rayon"]

            # prendre la première balle de la liste (étape 4 gérera les suivantes)
            params = self.config["balles"][0]
            balle = Balle(
                params["position_x"], params["position_y"],
                params["vitesse_x"],  params["vitesse_y"],
                mu, lf, hf, rf
            )

            # calculer la trajectoire de la balle
            self.trajectoire = balle.calculer_trajectoire()

            # afficher la position finale
            p_fin = self.trajectoire[-1]
            self.lbl_final.config(text=f"Position finale : ({p_fin[0]:.1f}, {p_fin[1]:.1f})")

            # démarrer l'animation depuis le début
            self.idx = 0
            self._animer()

        except ParametreInvalideError as e:  # gérer les exceptions personnalisées
            self.lbl_erreur.config(text=str(e))

    def _animer(self):
        # arrêter quand on a affiché tous les pas
        if self.idx >= len(self.trajectoire):
            return

        # récupérer la position du pas courant
        px, py = self.trajectoire[self.idx]
        cx, cy = px + BW, py + BW  # décalage pour les bandes visuelles

        # déplacer l'ovale sur le canevas
        self.canvas.coords(self.balle_dessin, cx-R, cy-R, cx+R, cy+R)

        self.idx += 1
        self.root.after(30, self._animer)  # rappeler _animer dans 30ms


# point d'entrée pour lancer la simulation
if __name__ == "__main__":
    Simulation()  # créer une instance de la classe Simulation pour lancer l'interface
