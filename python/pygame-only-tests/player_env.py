from game import Game
import pygame

class PlayerEnv:
    def __init__(self):
        self.game = Game()
        self.current_step = 0
        self.max_steps = 2500

    def reset(self):
        self.current_step = 0
        return self.game.reset()

    def step(self, action):
        self.current_step += 1
        state, reward, done = self.game.step(action)
        
        if self.current_step >= self.max_steps:
            return state, -75.0, True

        return state, reward, done

    def render(self):
        self.game.render()

    def close(self):
        pygame.quit()


if __name__ == "__main__":
    env = PlayerEnv()
    env.game.set_level('level1')
    state = env.reset()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        action = -1
        if keys[pygame.K_RIGHT]:
            action = 0
        elif keys[pygame.K_LEFT]:
            action = 1
        elif keys[pygame.K_UP]:
            action = 2
        elif keys[pygame.K_DOWN]:
            action = 3

        if action != -1:
            state, reward, done = env.step(action)
            print(f"Reward: {reward}, Done: {done}")

        env.render()

    env.close()