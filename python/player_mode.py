import pygame
from player_env import PlayerEnv

class PlayerMode:
    def __init__(self, screen, font, game, clock):
        self.screen = screen
        self.font = font
        self.game = game
        self.clock = clock
        self.env = PlayerEnv()

    def run(self):
        level = self.level_selection_menu()
        if level:
            return self.play_level(level)
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

    def play_level(self, level):
        self.env.set_level(level)
        state, reward, done = self.env.reset()
        total_reward = 0

        back_button = pygame.Rect(10, self.screen.get_height() - 60, 180, 40)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        return None

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
                state, reward, done = self.env.step(action)
                total_reward += reward

            self.screen.fill((0, 0, 0))
            self.env.render(self.screen)
            self.draw_text(f'Total Reward: {total_reward:.2f}', (self.screen.get_width() // 2, 30))

            # Draw back button
            pygame.draw.rect(self.screen, (100, 100, 100), back_button)
            self.draw_text("Back", back_button.center)

            pygame.display.flip()
            self.clock.tick(60)

            if done:
                break

        return self.game_over_menu(total_reward)

    def game_over_menu(self, total_reward):
        buttons = [
            pygame.Rect(450, 300, 300, 50),
            pygame.Rect(450, 400, 300, 50)
        ]

        back_button = pygame.Rect(10, self.screen.get_height() - 60, 180, 40)

        while True:
            self.screen.fill((0, 0, 0))
            self.draw_text('Game Over', (self.screen.get_width() // 2, 100))
            self.draw_text(f'Total Reward: {total_reward:.2f}', (self.screen.get_width() // 2, 200))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if buttons[0].collidepoint(event.pos):
                        return 'player'
                    elif buttons[1].collidepoint(event.pos):
                        return None
                    elif back_button.collidepoint(event.pos):
                        return None

            pygame.draw.rect(self.screen, (100, 100, 100), buttons[0])
            pygame.draw.rect(self.screen, (100, 100, 100), buttons[1])
            self.draw_text('Play Again', buttons[0].center)
            self.draw_text('Main Menu', buttons[1].center)

            # Draw back button
            pygame.draw.rect(self.screen, (100, 100, 100), back_button)
            self.draw_text("Back to Menu", back_button.center)

            pygame.display.flip()

    def draw_text(self, text, position):
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=position)
        self.screen.blit(text_surface, text_rect)