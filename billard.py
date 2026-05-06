import numpy as np

class Billard:
    def __init__(self, p, v):
        self.p = np.array(p)
        self.v = np.array(v)
    
    def position(self, t):
        return self.p + self.v * t
    
    def collision(self, r, h, l):
        p_min = np.array([r, r])
        p_max = np.array([l - r, h - r])

        # La balle touche un bord si :
        np.any(self.p <= p_min) or np.any(self.p >= p_max)
