from game import Game
import pygame

class PlayerEnv:
    def __init__(self):
        self.game = Game()
        self.current_step = 0
        self.max_steps = 1000

    def reset(self):
        self.current_step = 0
        return self.game.reset()

    def step(self, action):
        self.current_step += 1
        state, reward, done = self.game.step(action)

        if self.current_step >= self.max_steps:
            return state, -75.0, True

        return state, reward, done

    def render(self, surface):
        self.game.render(surface)

    def set_level(self, level_name):
        self.game.set_level(level_name)