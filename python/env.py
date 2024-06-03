import pygame
import time
import numpy as np
import random
from scipy.integrate import solve_ivp

class CartPoleEnv:
    def __init__(self):
        """
        constructeur
        """

        pygame.init()
        self.width, self.height = 600, 400
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        # Paramètres physiques
        self.m = 0.0001  # Masse du bâton
        self.mc = 1.0  # Masse de la plateforme
        self.l = 2.0  # Longueur du bâton (centre de masse à l'extrémité)
        self.g = 9.81  # Accélération due à la gravité
        self.scale = 100  # pixels par mètre
        self.framerate = 60
        self.last_frame_time = time.time()
        self.steps = 0
        self.angle_integral = 0
        self.ppos_integral = 0

        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (255, 0, 0)
        }

        # Conditions initiales
        self.reset()


    def reset(self):
        """
        Remet a 0 l'environnement.
        """
        self.y = [0, 0, random.uniform(-0.05, 0.05), 0]  # x, x_dot, theta, theta_dot
        self.u = 0
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
            self.u = -10  # Pousser à gauche
        elif action == 2:
            self.u = 10   # Pousser à droite
        else:
            self.u = 0    # Ne rien faire

        t_span = [0, 0.02]  # Interval for integration
        sol = solve_ivp(self.dynamics, t_span, self.y, args=(self.u,), rtol=1e-5)
        self.y = sol.y[:, -1]
        self.angle_integral += self.y[2]
        self.ppos_integral += self.y[0]

        game_over = False
        if abs(self.y[2]) > np.pi / 4 or abs(self.y[0]) > (self.width / 2 / self.scale):
            game_over = True

        if self.steps >= 10000:
            steps += 10000 # reward boost
            game_over = True

        return self.y, self.reward(), game_over

    def dynamics(self, t, y, u):
        x, x_dot, theta, theta_dot = y
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        total_mass = self.m + self.mc
        temp = (u + self.m * self.l * theta_dot ** 2 * sin_theta) / total_mass

        theta_ddot = (self.g * sin_theta - cos_theta * temp) / (self.l * (4/3 - self.m * cos_theta ** 2 / total_mass))
        x_ddot = temp - self.m * self.l * theta_ddot * cos_theta / total_mass

        return [x_dot, x_ddot, theta_dot, theta_ddot]



    def render(self, quick = True):
        """
        Affiche la frame actuelle

        Quick set sur true = unlimited tickrate

        (imo cette partie sera dans godot, a voir)
        """

        self.screen.fill(self.colors['white'])
        pygame.draw.rect(self.screen, self.colors['black'], [self.width/2 + self.y[0]*self.scale - 50, self.height/2 - 10, 100, 20])
        pole_end = (self.width/2 + self.y[0]*self.scale + self.l*self.scale*np.sin(self.y[2]), self.height/2 - self.l*self.scale*np.cos(self.y[2]))
        pygame.draw.line(self.screen, self.colors['red'], (self.width/2 + self.y[0]*self.scale, self.height/2), pole_end, 5)
        next_frame_time = self.last_frame_time + 1/self.framerate
        #time.sleep(max(0, next_frame_time - time.time()))
        if not quick:
            time.sleep(1/self.framerate)
        pygame.display.flip()

    def reward(self):
        """
        retourne la reward totale depuis le debut de l'episode
        """
        return - abs(self.angle_integral) + self.steps/30



    def close(self):
        """
        selfexplanatory
        """
        pygame.quit()
