import pygame
import time
import os
from player_env import PlayerEnv
from agents.ppo import Agent

class AIMode:
    def __init__(self, screen, font, game, clock):
        self.screen = screen
        self.font = font
        self.game = game
        self.clock = clock
        self.env = PlayerEnv()
        self.agent = Agent(nb_actions=4, batch_size=1024, alpha=0.0003, nb_epochs=4, input_dims=(10,))
        self.agent.models_dir = "models_data"
        
        # Define layout constants
        self.left_panel_width = 200
        self.right_panel_width = 200
        self.game_area_width = self.screen.get_width() - self.left_panel_width - self.right_panel_width
        self.game_area_height = self.screen.get_height()
        self.game_area_left = self.left_panel_width

    def run(self):
        level = self.level_selection_menu()
        if level:
            return self.train_ai(level)
        return None

    def level_selection_menu(self):
        buttons = []
        button_height = 50
        button_width = 300
        start_y = 100
        max_buttons = 8
        scroll_offset = 0

        back_button = pygame.Rect(10, self.screen.get_height() - 60, 180, 40)

        while True:
            self.screen.fill((0, 0, 0))
            self.draw_text('Select Level', (self.screen.get_width() // 2, 50))
            self.draw_text('Warning: PyTorch will load causing a lagspike, don\'t panic', (self.screen.get_width() // 2, 80), color=(255, 255, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        for i, button in enumerate(buttons):
                            if button.collidepoint(event.pos):
                                return list(self.game.levels.keys())[i + scroll_offset]
                        if back_button.collidepoint(event.pos):
                            return None
                    elif event.button == 4:  # Scroll up
                        scroll_offset = max(0, scroll_offset - 1)
                    elif event.button == 5:  # Scroll down
                        scroll_offset = min(len(self.game.levels) - max_buttons, scroll_offset + 1)

            buttons = []
            for i, level_name in enumerate(list(self.game.levels.keys())[scroll_offset:scroll_offset + max_buttons]):
                button = pygame.Rect(self.screen.get_width() // 2 - button_width // 2, start_y + i * (button_height + 10), button_width, button_height)
                buttons.append(button)
                pygame.draw.rect(self.screen, (100, 100, 100), button)
                self.draw_text(level_name, button.center)

            # Draw scroll indicators
            if scroll_offset > 0:
                self.draw_text("↑", (self.screen.get_width() // 2, start_y - 20))
            if scroll_offset + max_buttons < len(self.game.levels):
                self.draw_text("↓", (self.screen.get_width() // 2, start_y + max_buttons * (button_height + 10) + 20))

            # Draw back button
            pygame.draw.rect(self.screen, (100, 100, 100), back_button)
            self.draw_text("Back", back_button.center)

            pygame.display.flip()

    def train_ai(self, level):
        self.env.set_level(level)
        state, _, _ = self.env.reset()

        stats = {
            "current_reward": 0,
            "current_loss_actor": 0,
            "current_loss_critic": 0,
            "episode": 1,
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

        # Adjust button positions
        button_width = 180
        button_height = 40
        button_margin = 10
        pause_button = pygame.Rect(button_margin, button_margin, button_width, button_height)
        render_button = pygame.Rect(button_margin, pause_button.bottom + button_margin, button_width, button_height)
        load_button = pygame.Rect(button_margin, self.screen.get_height() - 3 * (button_height + button_margin), button_width, button_height)
        save_button = pygame.Rect(button_margin, self.screen.get_height() - 2 * (button_height + button_margin), button_width, button_height)
        back_button = pygame.Rect(button_margin, self.screen.get_height() - (button_height + button_margin), button_width, button_height)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
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
                            return None
                        elif save_button.collidepoint(event.pos):
                            self.save_model()
                        elif load_button.collidepoint(event.pos):
                            self.load_model()

            if not paused:
                action, prob, val = self.agent.choose_action(state)
                next_state, reward, done = self.env.step(action)

                stats["current_reward"] += reward
                stats["time_steps"] += 1
                stats["session_time"] = time.time() - start_time
                stats["episode_time"] = time.time() - episode_start_time
                stats["real_time_equivalent"] = stats["time_steps"] / 60

                self.agent.remember(state, action, prob, val, reward, done)

                if stats["time_steps"] % 1024 == 0:
                    self.agent.learn()
                    stats["learning_steps"] += 1
                    stats["current_loss_actor"] = self.agent.actor_loss
                    stats["current_loss_critic"] = self.agent.critic_loss

                if done:
                    stats["episode"] += 1
                    stats["current_reward"] = 0
                    episode_start_time = time.time()
                    state, _, _ = self.env.reset()
                else:
                    state = next_state

            self.screen.fill((0, 0, 0))

            # Draw left panel
            pygame.draw.rect(self.screen, (50, 50, 50), (0, 0, self.left_panel_width, self.screen.get_height()))

            # Draw game area
            game_surface = pygame.Surface((self.game_area_width, self.game_area_height))
            if render_game:
                self.env.render(game_surface)
            self.screen.blit(game_surface, (self.game_area_left, 0))

            # Draw right panel (for stats)
            pygame.draw.rect(self.screen, (50, 50, 50), (self.screen.get_width() - self.right_panel_width, 0, self.right_panel_width, self.screen.get_height()))

            self.draw_stats(stats)
            self.draw_control_panel(paused, render_game, pause_button, render_button, load_button, save_button, back_button)

            pygame.display.flip()
            self.clock.tick(60)

    def draw_stats(self, stats):
        y = 10
        for key, value in stats.items():
            if isinstance(value, float):
                text = f"{key}: {value:.2f}"
            else:
                text = f"{key}: {value}"
            self.draw_text(text, (self.screen.get_width() - self.right_panel_width + 10, y), align="left")
            y += 30

    def draw_control_panel(self, paused, render_game, pause_button, render_button, load_button, save_button, back_button):
        # Draw buttons
        pygame.draw.rect(self.screen, (255, 0, 0) if paused else (0, 255, 0), pause_button)
        pygame.draw.rect(self.screen, (255, 0, 0) if not render_game else (0, 255, 0), render_button)
        pygame.draw.rect(self.screen, (100, 100, 100), load_button)
        pygame.draw.rect(self.screen, (100, 100, 100), save_button)
        pygame.draw.rect(self.screen, (100, 100, 100), back_button)

        self.draw_text("Pause/Resume", pause_button.center, color=(0, 0, 0))
        self.draw_text("Toggle Render", render_button.center, color=(0, 0, 0))
        self.draw_text("Load Model", load_button.center)
        self.draw_text("Save Model", save_button.center)
        self.draw_text("Back to Menu", back_button.center)

    def draw_text(self, text, position, color=(255, 255, 255), align="center"):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "center":
            text_rect.center = position
        elif align == "left":
            text_rect.midleft = position
        self.screen.blit(text_surface, text_rect)

    def save_model(self):
        filename = self.text_input("Enter model name to save:")
        if filename:
            self.agent.save_models(filename)
            print(f"Model saved as {filename}")

    def load_model(self):
        available_models = self.agent.get_available_models()
        if not available_models:
            print("No saved models found.")
            return

        selected_model = self.selection_menu("Select a model to load:", available_models)
        if selected_model:
            self.agent.load_models(selected_model)
            print(f"Model {selected_model} loaded")

    def text_input(self, prompt):
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

            self.screen.fill((0, 0, 0))
            self.draw_text(prompt, (self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
            pygame.draw.rect(self.screen, (100, 100, 100), (self.screen.get_width() // 2 - 100, self.screen.get_height() // 2, 200, 40))
            self.draw_text(input_text, (self.screen.get_width() // 2, self.screen.get_height() // 2 + 20))
            pygame.display.flip()

        return input_text

    def selection_menu(self, prompt, options):
        buttons = []
        button_height = 50
        button_width = 300
        start_y = 100
        max_buttons = 8
        scroll_offset = 0

        back_button = pygame.Rect(10, self.screen.get_height() - 60, 180, 40)

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

            self.screen.fill((0, 0, 0))
            self.draw_text(prompt, (self.screen.get_width() // 2, 50))

            buttons = []
            for i, option in enumerate(options[scroll_offset:scroll_offset + max_buttons]):
                button = pygame.Rect(self.screen.get_width() // 2 - button_width // 2, start_y + i * (button_height + 10), button_width, button_height)
                buttons.append(button)
                mouse_pos = pygame.mouse.get_pos()
                color = (150, 150, 150) if button.collidepoint(mouse_pos) else (100, 100, 100)
                pygame.draw.rect(self.screen, color, button)
                self.draw_text(option, button.center)

            # Draw scroll indicators
            if scroll_offset > 0:
                self.draw_text("↑", (self.screen.get_width() // 2, start_y - 20))
            if scroll_offset + max_buttons < len(options):
                self.draw_text("↓", (self.screen.get_width() // 2, start_y + max_buttons * (button_height + 10) + 20))

            # Draw back button
            pygame.draw.rect(self.screen, (100, 100, 100), back_button)
            self.draw_text("Back", back_button.center)

            pygame.display.flip()