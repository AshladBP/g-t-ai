import numpy as np
from godot_websocket import *

class GodotEnv:
    def __init__(self):
        """
        constructeur
        """
        self.action = 0
        self.steps = 0
        # Conditions initiales
        self.reset()


    def reset(self):
        """
        Remet a 0 l'environnement.
        """
        self.state = []  # x, x_dot, theta, theta_dot
        self.action = 0
        self.steps = 0
        self.angle_integral = 0
        self.ppos_integral = 0
        return self.y


    def step(self, action):
        """
        Prends en entrée une action, et avance d'une frame.

        Retourne:
            - La nouvelle observation
            - la reward
            - un booleen qui dit si la partie est terminée ou non 
        """
        self.steps += 1
        if action == 1:
            # A gauche
            pass
        elif action == 2:
            # A droite
            pass
        elif action == 3:
            # En haut
            pass
        elif action == 4:
            # En bas
            pass
        else:
            # Ne rien faire
            pass

        if self.steps >= 10000:
            steps += 10000 # reward boost
            game_over = True

        return self.state, self.reward(), game_over

    def dynamics(self, t, y, u):
        x, x_dot, theta, theta_dot = y
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        total_mass = self.m + self.mc
        temp = (u + self.m * self.l * theta_dot ** 2 * sin_theta) / total_mass

        theta_ddot = (self.g * sin_theta - cos_theta * temp) / (self.l * (4/3 - self.m * cos_theta ** 2 / total_mass))
        x_ddot = temp - self.m * self.l * theta_ddot * cos_theta / total_mass

        return [x_dot, x_ddot, theta_dot, theta_ddot]

    def reward(self):
        """
        retourne la reward totale depuis le debut de l'episode
        """
        return - abs(self.angle_integral) + self.steps/30



    def close(self):
        """
        selfexplanatory
        """
        pass
