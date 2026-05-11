import tkinter as tk
import numpy as np

fenetre = tk.Tk()
fenetre.title("Billard")

tk.Label(fenetre, text="Entrez une vitesse initiale:").pack()
vitesse_ini = tk.Entry(fenetre)
vitesse_ini.pack()

tk.Label(fenetre, text="Entrez un angle de tir:").pack()
angle = tk.Entry(fenetre)
angle.pack()

compteur = 0
x = 200
y = 200
temps = 0

def lancement():
    global x, y

    v = float(vitesse_ini.get())
    a = float(angle.get())
    position_initiale = np.array([200, 200])
    vitesse_initiale = np.array([v * np.cos(np.radians(a)), v * np.sin(np.radians(a))])

    for i in vitesse_initiale:
        vitesse_x_temps = [i * 5, i * 5]
        position_finale = [x + y for x, y in zip(position_initiale, vitesse_x_temps)]

    x = position_finale[0]
    y = position_finale[1]
    surface.create_oval(200+9, 200+9, 200-9, 200-9, fill="white", outline="black", tags="ball")

    def pas_suivant():
        global temps
        if temps < 5:
            temps += 1
            for i in vitesse_initiale:
                vitesse_x_temps = [i * temps, i * temps]
                position_finale = [x + y for x, y in zip(position_initiale, vitesse_x_temps)]

            p_min = np.array([9, 9])
            p_max = np.array([488 - 9, 270 - 9])

            if np.any(position_finale <= p_min) or np.any(position_finale >= p_max):
                return

            x = position_finale[0]
            y = position_finale[1]

            surface.delete("ball")
            surface.create_oval(x+9, y+9, x-9, y-9, fill="white", outline="black", tags="ball")

        else:
            temps = 5
            for i in vitesse_initiale:
                vitesse_x_temps = [i * temps, i * temps]
                position_finale = [x + y for x, y in zip(position_initiale, vitesse_x_temps)]
            
            p_min = np.array([9, 9])
            p_max = np.array([488 - 9, 270 - 9])

            if np.any(position_finale <= p_min) or np.any(position_finale >= p_max):
                temps -= 1
                return

            x = position_finale[0]
            y = position_finale[1]

            surface.delete("ball")
            surface.create_oval(x+9, y+9, x-9, y-9, fill="white", outline="black", tags="ball")

    
    def pas_precedent():
        global temps
        if temps > 0:
            temps -= 1
            for i in vitesse_initiale:
                vitesse_x_temps = [i * temps, i * temps]
                position_finale = [x + y for x, y in zip(position_initiale, vitesse_x_temps)]

            x = position_finale[0]
            y = position_finale[1]
            surface.delete("ball")
            surface.create_oval(x+9, y+9, x-9, y-9, fill="white", outline="black", tags="ball")

        else:
            temps = 0
            for i in vitesse_initiale:
                vitesse_x_temps = [i * temps, i * temps]
                position_finale = [x + y for x, y in zip(position_initiale, vitesse_x_temps)]

            x = position_finale[0]
            y = position_finale[1]
            surface.delete("ball")
            surface.create_oval(x+9, y+9, x-9, y-9, fill="white", outline="black", tags="ball")
    
    def position_finale_bouton():
        surface.delete("ball")
        surface.create_oval(x+9, y+9, x-9, y-9, fill="white", outline="black", tags="ball")
    
    def reinitialiser():
        surface.delete("ball")
        surface.create_oval(200+9, 200+9, 200-9, 200-9, fill="white", outline="black", tags="ball")

    global compteur
    compteur += 1
    if compteur > 0:
        compteur = 0
        tk.Button(fenetre, text="Pas suivant", command=pas_suivant).pack()
        tk.Button(fenetre, text="Pas précédent", command=pas_precedent).pack()
        tk.Button(fenetre, text="Position finale", command=position_finale_bouton).pack()
        tk.Button(fenetre, text="Réinitialiser", command=reinitialiser).pack()
    
lancer = tk.Button(fenetre, text="Lancer", command=lancement)
lancer.pack()

surface = tk.Canvas(fenetre, width=488, height=270, bg="green", highlightthickness=4, highlightbackground="black")
surface.pack()

tk.mainloop()