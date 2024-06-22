import pygame
import random
from game import Game
from player_env import PlayerEnv

def main():
    pygame.init()
    game = Game()
    
    running = True
    while running:
        level, mode = game.main_menu()
        
        if level is None or mode is None:
            running = False
            continue

        env = PlayerEnv()
        env.game.set_level(level)
        state, reward, done = env.reset()

        total_reward = 0
        game_running = True
        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                    running = False

            if mode == 'player':
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
            else:  # AI mode
                action = random.randint(0, 3)

            if action != -1:
                state, reward, done = env.step(action)
                total_reward += reward
                print(f"Reward: {reward}, Total Reward: {total_reward}, Done: {done}")

            env.render()

            if done:
                game_running = False


        # Game over menu
        game_over_choice = game.game_over_menu(total_reward)
        if game_over_choice == 'quit':
            running = False
        elif game_over_choice == 'main_menu':
            continue
        elif game_over_choice == 'play_again':
            pass
            # The outer loop will automatically start a new game with the same level and mode

    pygame.quit()

if __name__ == "__main__":
    main()