import pygame
import os
from game import Game
from player_env import PlayerEnv
from agents.ppo import Agent
from level_editor import LevelEditor
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

    game = Game()
    env = PlayerEnv()

    running = True
    mode = main_menu(screen, font)

    while running:
        if mode is None:
            running = False
            continue

        if mode == 'player':
            level = level_selection_menu(screen, font, game.levels)
            if level:
                player_mode(screen, font, env, clock, level)
            else:
                mode = main_menu(screen, font)
                continue
        elif mode == 'ai':
            level = level_selection_menu(screen, font, game.levels, ai_mode=True)
            if level:
                ai_mode(screen, font, env, clock, level)
            else:
                mode = main_menu(screen, font)
                continue
        elif mode == 'editor':
            level_editor = LevelEditor(GAME_WIDTH, GAME_HEIGHT)
            level_editor.run(screen, clock)
            game.levels = game.load_all_levels()  # Reload levels after editing

        mode = main_menu(screen, font)
    pygame.quit()

def main_menu(screen, font):
    buttons = [
        pygame.Rect(450, 150, 300, 50),
        pygame.Rect(450, 250, 300, 50),
        pygame.Rect(450, 350, 300, 50)
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
                elif buttons[2].collidepoint(event.pos):
                    return 'editor'

        pygame.draw.rect(screen, (100, 100, 100), buttons[0])
        pygame.draw.rect(screen, (100, 100, 100), buttons[1])
        pygame.draw.rect(screen, (100, 100, 100), buttons[2])
        draw_text(screen, font, 'Player Mode', (255, 255, 255), buttons[0].center)
        draw_text(screen, font, 'AI Mode', (255, 255, 255), buttons[1].center)
        draw_text(screen, font, 'Level Editor', (255, 255, 255), buttons[2].center)

        pygame.display.flip()

def level_selection_menu(screen, font, levels, ai_mode=False):
    buttons = []
    button_height = 50
    button_width = 300
    start_y = 100
    max_buttons = 8
    scroll_offset = 0

    back_button = pygame.Rect(10, SCREEN_HEIGHT - 60, 180, 40)

    while True:
        screen.fill((0, 0, 0))
        draw_text(screen, font, 'Select Level', (255, 255, 255), (SCREEN_WIDTH // 2, 50))

        if ai_mode:
            draw_text(screen, font, 'Warning: PyTorch will load causing a lagspike, don\'t panic', (255, 255, 0), (SCREEN_WIDTH // 2, 80))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    for i, button in enumerate(buttons):
                        if button.collidepoint(event.pos):
                            return list(levels.keys())[i + scroll_offset]
                    if back_button.collidepoint(event.pos):
                        return None
                elif event.button == 4:  # Scroll up
                    scroll_offset = max(0, scroll_offset - 1)
                elif event.button == 5:  # Scroll down
                    scroll_offset = min(len(levels) - max_buttons, scroll_offset + 1)

        buttons = []
        for i, level_name in enumerate(list(levels.keys())[scroll_offset:scroll_offset + max_buttons]):
            button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + i * (button_height + 10), button_width, button_height)
            buttons.append(button)
            pygame.draw.rect(screen, (100, 100, 100), button)
            draw_text(screen, font, level_name, (255, 255, 255), button.center)

        # Draw scroll indicators
        if scroll_offset > 0:
            draw_text(screen, font, "↑", (255, 255, 255), (SCREEN_WIDTH // 2, start_y - 20))
        if scroll_offset + max_buttons < len(levels):
            draw_text(screen, font, "↓", (255, 255, 255), (SCREEN_WIDTH // 2, start_y + max_buttons * (button_height + 10) + 20))

        # Draw back button
        pygame.draw.rect(screen, (100, 100, 100), back_button)
        draw_text(screen, font, "Back", (255, 255, 255), back_button.center)

        pygame.display.flip()

def player_mode(screen, font, env, clock, level):
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    env.set_level(level)
    state, reward, done = env.reset()
    total_reward = 0

    back_button = pygame.Rect(10, SCREEN_HEIGHT - 60, 180, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
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

        # Draw back button
        pygame.draw.rect(screen, (100, 100, 100), back_button)
        draw_text(screen, font, "Back", (255, 255, 255), back_button.center)

        pygame.display.flip()
        clock.tick(60)

        if done:
            break

    game_over_menu(screen, font, total_reward)

def ai_mode(screen, font, env, clock, level):
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    env.set_level(level)
    agent = Agent(nb_actions=4, batch_size=1024, alpha=0.0003, nb_epochs=4, input_dims=(10,))
    agent.models_dir = "models_data"
    stats = {
        "current_reward": 0,
        "current_loss_actor": 0,
        "current_loss_critic": 0,
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
    save_button = pygame.Rect(10, SCREEN_HEIGHT - 110, 180, 40)
    load_button = pygame.Rect(10, SCREEN_HEIGHT - 160, 180, 40)
    pause_button = pygame.Rect(10, SCREEN_HEIGHT - 210, 180, 40)
    render_button = pygame.Rect(10, SCREEN_HEIGHT - 260, 180, 40)

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
                    elif save_button.collidepoint(event.pos):
                        save_model(screen, font, agent)
                    elif load_button.collidepoint(event.pos):
                        load_model(screen, font, agent)

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

        pygame.draw.rect(screen, (100, 100, 100), save_button)
        draw_text(screen, font, "Save Model", (255, 255, 255), save_button.center)

        pygame.draw.rect(screen, (100, 100, 100), load_button)
        draw_text(screen, font, "Load Model", (255, 255, 255), load_button.center)

        pygame.display.flip()
        clock.tick(60)

def save_model(screen, font, agent):
    filename = text_input(screen, font, "Enter model name to save:")
    if filename:
        agent.save_models(filename)
        print(f"Model saved as {filename}")

def load_model(screen, font, agent):
    available_models = agent.get_available_models()
    if not available_models:
        print("No saved models found.")
        return

    selected_model = selection_menu(screen, font, "Select a model to load:", available_models)
    if selected_model:
        agent.load_models(selected_model)
        print(f"Model {selected_model} loaded")


def text_input(screen, font, prompt):
    input_text = ""
    input_active = True
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        screen.fill((0, 0, 0))
        draw_text(screen, font, prompt, (255, 255, 255), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        pygame.draw.rect(screen, (100, 100, 100), (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 40))
        draw_text(screen, font, input_text, (255, 255, 255), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        pygame.display.flip()

    return input_text

def selection_menu(screen, font, prompt, options):
    buttons = []
    button_height = 50
    button_width = 300
    start_y = 100
    max_buttons = 8
    scroll_offset = 0

    back_button = pygame.Rect(10, SCREEN_HEIGHT - 60, 180, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    for i, button in enumerate(buttons):
                        if button.collidepoint(mouse_pos):
                            return options[i + scroll_offset]
                    if back_button.collidepoint(mouse_pos):
                        return None
                elif event.button == 4:  # Scroll up
                    scroll_offset = max(0, scroll_offset - 1)
                elif event.button == 5:  # Scroll down
                    scroll_offset = min(len(options) - max_buttons, scroll_offset + 1)

        screen.fill((0, 0, 0))
        draw_text(screen, font, prompt, (255, 255, 255), (SCREEN_WIDTH // 2, 50))

        buttons = []
        for i, option in enumerate(options[scroll_offset:scroll_offset + max_buttons]):
            button = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + i * (button_height + 10), button_width, button_height)
            buttons.append(button)
            mouse_pos = pygame.mouse.get_pos()
            color = (150, 150, 150) if button.collidepoint(mouse_pos) else (100, 100, 100)
            pygame.draw.rect(screen, color, button)
            draw_text(screen, font, option, (255, 255, 255), button.center)

        # Draw scroll indicators
        if scroll_offset > 0:
            draw_text(screen, font, "↑", (255, 255, 255), (SCREEN_WIDTH // 2, start_y - 20))
        if scroll_offset + max_buttons < len(options):
            draw_text(screen, font, "↓", (255, 255, 255), (SCREEN_WIDTH // 2, start_y + max_buttons * (button_height + 10) + 20))

        # Draw back button
        pygame.draw.rect(screen, (100, 100, 100), back_button)
        draw_text(screen, font, "Back", (255, 255, 255), back_button.center)

        pygame.display.flip()

def draw_stats(screen, font, stats):
    y = 10
    for key, value in stats.items():
        if isinstance(value, float):
            text = f"{key}: {value:.2f}"
        else:
            text = f"{key}: {value}"
        draw_text(screen, font, text, (255, 255, 255), (SCREEN_WIDTH - 100, y))
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

    back_button = pygame.Rect(10, SCREEN_HEIGHT - 60, 180, 40)

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
                elif back_button.collidepoint(event.pos):
                    return 'main_menu'

        pygame.draw.rect(screen, (100, 100, 100), buttons[0])
        pygame.draw.rect(screen, (100, 100, 100), buttons[1])
        draw_text(screen, font, 'Play Again', (255, 255, 255), buttons[0].center)
        draw_text(screen, font, 'Main Menu', (255, 255, 255), buttons[1].center)

        # Draw back button
        pygame.draw.rect(screen, (100, 100, 100), back_button)
        draw_text(screen, font, "Back to Menu", (255, 255, 255), back_button.center)

        pygame.display.flip()

def draw_text(screen, font, text, color, position):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=position)
    screen.blit(text_surface, text_rect)

if __name__ == "__main__":
    main()