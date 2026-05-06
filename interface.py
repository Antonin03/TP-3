import tkinter as tk
from billard import Billard
import numpy as np

fenetre = tk.Tk()
fenetre.title("Billard")

tk.Label(fenetre, text="Entrez une vitesse initiale:").pack()
vitesse_ini = tk.Entry(fenetre)
vitesse_ini.pack()

tk.Label(fenetre, text="Entrez un angle de tir:").pack()
angle = tk.Entry(fenetre)
angle.pack()

def lancement():
    v = float(vitesse_ini.get())
    a = float(angle.get())
    position_initiale = np.array([200, 200])
    vitesse_initiale = np.array([v * np.cos(np.radians(a)), v * np.sin(np.radians(a))])
    position_balle = position_initiale + vitesse_initiale * 5

tk.Button(fenetre, text="Lancer", command=lancement).pack()

surface = tk.Canvas(fenetre, width=488, height=270, bg="green", highlightthickness=4, highlightbackground="black")
surface.pack()

surface.coords("ball", x-5, y-5, x+5, y+5)
surface.create_oval(5, 5, 5, 5, fill="white", outline="black", tags="ball")

tk.mainloop()
