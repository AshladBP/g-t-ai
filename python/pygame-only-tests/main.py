import pygame
import random
from game import Game
from player_env import PlayerEnv
from agents.ppo import Agent
import numpy as np
import time

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
GAME_WIDTH = 800
GAME_HEIGHT = 600

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("AI Training Environment")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    env = PlayerEnv()

    running = True
    mode = main_menu(screen, font)

    while running:
        if mode is None:
            running = False
            continue

        if mode == 'player':
            player_mode(screen, font, env, clock)
        elif mode == 'ai':
            level = level_selection_menu(screen, font)
            if level:
                ai_mode(screen, font, env, clock, level)
            else:
                mode = main_menu(screen, font)
                continue

        mode = main_menu(screen, font)

    pygame.quit()

def main_menu(screen, font):
    buttons = [
        pygame.Rect(450, 200, 300, 50),
        pygame.Rect(450, 300, 300, 50)
    ]

    while True:
        screen.fill((0, 0, 0))
        draw_text(screen, font, 'Main Menu', (255, 255, 255), (SCREEN_WIDTH // 2, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].collidepoint(event.pos):
                    return 'player'
                elif buttons[1].collidepoint(event.pos):
                    return 'ai'

        pygame.draw.rect(screen, (100, 100, 100), buttons[0])
        pygame.draw.rect(screen, (100, 100, 100), buttons[1])
        draw_text(screen, font, 'Player Mode', (255, 255, 255), buttons[0].center)
        draw_text(screen, font, 'AI Mode', (255, 255, 255), buttons[1].center)

        pygame.display.flip()

def level_selection_menu(screen, font):
    buttons = [
        pygame.Rect(450, 200, 300, 50),
        pygame.Rect(450, 300, 300, 50),
        pygame.Rect(450, 400, 300, 50)
    ]

    while True:
        screen.fill((0, 0, 0))
        draw_text(screen, font, 'Select Level', (255, 255, 255), (SCREEN_WIDTH // 2, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].collidepoint(event.pos):
                    return 'level1'
                elif buttons[1].collidepoint(event.pos):
                    return 'level2'
                elif buttons[2].collidepoint(event.pos):
                    return None

        pygame.draw.rect(screen, (100, 100, 100), buttons[0])
        pygame.draw.rect(screen, (100, 100, 100), buttons[1])
        pygame.draw.rect(screen, (100, 100, 100), buttons[2])
        draw_text(screen, font, 'Level 1', (255, 255, 255), buttons[0].center)
        draw_text(screen, font, 'Level 2', (255, 255, 255), buttons[1].center)
        draw_text(screen, font, 'Back to Main Menu', (255, 255, 255), buttons[2].center)

        pygame.display.flip()

def player_mode(screen, font, env, clock):
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    state, reward, done = env.reset()
    total_reward = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

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
            total_reward += reward

        screen.fill((0, 0, 0))
        env.render(game_surface)
        screen.blit(game_surface, (200, 0))
        draw_text(screen, font, f'Total Reward: {total_reward:.2f}', (255, 255, 255), (SCREEN_WIDTH // 2, 30))

        pygame.display.flip()
        clock.tick(60)

        if done:
            break

    game_over_menu(screen, font, total_reward)

def ai_mode(screen, font, env, clock, level):
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    env.set_level(level)
    agent = Agent(nb_actions=4, batch_size=1024, alpha=0.0003, nb_epochs=4, input_dims=(10,))

    stats = {
        "current_reward": 0,
        "current_loss_actor": 0,
        "current_loss_critic": 0,
        "observation": [],
        "episode": 0,
        "time_steps": 0,
        "learning_steps": 0,
        "session_time": 0,
        "episode_time": 0,
        "real_time_equivalent": 0,
    }

    paused = False
    render_game = True
    start_time = time.time()
    episode_start_time = time.time()

    # Initialize the environment
    state, _, _ = env.reset()

    back_button = pygame.Rect(10, SCREEN_HEIGHT - 60, 180, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    render_game = not render_game
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if pause_button.collidepoint(event.pos):
                        paused = not paused
                    elif render_button.collidepoint(event.pos):
                        render_game = not render_game
                    elif back_button.collidepoint(event.pos):
                        return

        if not paused:
            action, prob, val = agent.choose_action(state)
            next_state, reward, done = env.step(action)

            stats["current_reward"] += reward
            stats["time_steps"] += 1
            stats["session_time"] = time.time() - start_time
            stats["episode_time"] = time.time() - episode_start_time
            stats["real_time_equivalent"] = stats["time_steps"] / 60

            agent.remember(state, action, prob, val, reward, done)

            if stats["time_steps"] % 1024 == 0:
                agent.learn()
                stats["learning_steps"] += 1
                stats["current_loss_actor"] = agent.actor_loss
                stats["current_loss_critic"] = agent.critic_loss

            if done:
                stats["episode"] += 1
                stats["current_reward"] = 0
                episode_start_time = time.time()
                state, _, _ = env.reset()
            else:
                state = next_state

        screen.fill((0, 0, 0))

        if render_game:
            env.render(game_surface)
            screen.blit(game_surface, (200, 0))

        draw_stats(screen, font, stats)
        pause_button, render_button = draw_control_panel(screen, font, paused, render_game)

        pygame.draw.rect(screen, (100, 100, 100), back_button)
        draw_text(screen, font, "Back to Menu", (255, 255, 255), back_button.center)

        pygame.display.flip()

def draw_stats(screen, font, stats):
    y = 10
    for key, value in stats.items():
        if isinstance(value, float):
            text = f"{key}: {value:.2f}"
        else:
            text = f"{key}: {value}"
        draw_text(screen, font, text, (255, 255, 255), (SCREEN_WIDTH - 200, y))
        y += 30

def draw_control_panel(screen, font, paused, render_game):
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, 200, SCREEN_HEIGHT))

    pause_button = pygame.Rect(10, 10, 180, 40)
    render_button = pygame.Rect(10, 60, 180, 40)

    pygame.draw.rect(screen, (255, 0, 0) if paused else (0, 255, 0), pause_button)
    pygame.draw.rect(screen, (255, 0, 0) if not render_game else (0, 255, 0), render_button)

    draw_text(screen, font, "Pause/Resume", (0, 0, 0), pause_button.center)
    draw_text(screen, font, "Toggle Render", (0, 0, 0), render_button.center)

    return pause_button, render_button

def game_over_menu(screen, font, total_reward):
    buttons = [
        pygame.Rect(450, 300, 300, 50),
        pygame.Rect(450, 400, 300, 50)
    ]

    while True:
        screen.fill((0, 0, 0))
        draw_text(screen, font, 'Game Over', (255, 255, 255), (SCREEN_WIDTH // 2, 100))
        draw_text(screen, font, f'Total Reward: {total_reward:.2f}', (255, 255, 255), (SCREEN_WIDTH // 2, 200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0].collidepoint(event.pos):
                    return
                elif buttons[1].collidepoint(event.pos):
                    return 'main_menu'

        pygame.draw.rect(screen, (100, 100, 100), buttons[0])
        pygame.draw.rect(screen, (100, 100, 100), buttons[1])
        draw_text(screen, font, 'Play Again', (255, 255, 255), buttons[0].center)
        draw_text(screen, font, 'Main Menu', (255, 255, 255), buttons[1].center)

        pygame.display.flip()

def draw_text(screen, font, text, color, position):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    main()