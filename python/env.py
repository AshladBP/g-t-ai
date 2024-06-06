import pygame
import time
import numpy as np
import random
from scipy.integrate import solve_ivp

class CartPoleEnv:
    def __init__(self):
        """
        Constructor
        """
        pygame.init()
        self.width, self.height = 600, 400
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()

        # Physical parameters (adjusted to match OpenAI Gym)
        self.m = 0.1  # Mass of the pole
        self.mc = 1.0  # Mass of the cart
        self.l = 0.5  # Length of the pole (from the pivot point to the end)
        self.g = 9.8  # Acceleration due to gravity
        self.force_mag = 10.0  # Magnitude of the applied force
        self.tau = 0.02  # Time interval for updates

        self.scale = 100  # Pixels per meter
        self.framerate = 60
        self.last_frame_time = time.time()

        self.colors = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (255, 0, 0)
        }

        # Initial conditions
        self.reset()

    def reset(self):
        """
        Reset the environment.
        """
        self.state = [0, 0, random.uniform(-0.05, 0.05), 0]  # x, x_dot, theta, theta_dot
        self.steps = 0
        return np.array(self.state)

    def step(self, action):
        """
        Take an action and advance one frame.

        Returns:
            - The new observation
            - The reward
            - A boolean indicating if the episode is done
        """
        self.steps += 1

        # Apply force based on action
        force = self.force_mag if action == 1 else -self.force_mag if action == 2 else 0

        # Update state using the dynamics
        t_span = [0, self.tau]
        sol = solve_ivp(self.dynamics, t_span, self.state, args=(force,), rtol=1e-5)
        self.state = sol.y[:, -1]

        x, x_dot, theta, theta_dot = self.state
        done = x < -2.4 or x > 2.4 or theta < -np.pi / 15 or theta > np.pi / 15 or self.steps >= 200

        reward = 1.0 if not done else 0.0

        return np.array(self.state), reward, done

    def dynamics(self, t, y, u):
        x, x_dot, theta, theta_dot = y
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        total_mass = self.m + self.mc
        temp = (u + self.m * self.l * theta_dot ** 2 * sin_theta) / total_mass

        theta_ddot = (self.g * sin_theta - cos_theta * temp) / (self.l * (4/3 - self.m * cos_theta ** 2 / total_mass))
        x_ddot = temp - self.m * self.l * theta_ddot * cos_theta / total_mass

        return [x_dot, x_ddot, theta_dot, theta_ddot]

    def render(self):
        """
        Render the current frame.
        """
        self.screen.fill(self.colors['white'])
        pygame.draw.rect(self.screen, self.colors['black'], [self.width/2 + self.state[0]*self.scale - 50, self.height/2 - 10, 100, 20])
        pole_end = (self.width/2 + self.state[0]*self.scale + self.l*self.scale*np.sin(self.state[2]), self.height/2 - self.l*self.scale*np.cos(self.state[2]))
        pygame.draw.line(self.screen, self.colors['red'], (self.width/2 + self.state[0]*self.scale, self.height/2), pole_end, 5)

        time.sleep(1 / self.framerate)
        pygame.display.flip()

    def close(self):
        """
        Close the environment.
        """
        pygame.quit()
