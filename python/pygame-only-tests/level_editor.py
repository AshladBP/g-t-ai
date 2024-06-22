import pygame
import json
import os

class LevelEditor:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        self.spawn = None
        self.goals = []
        self.current_tool = 'spawn'
        self.colors = {
            'background': (0, 0, 0),
            'wall': (255, 0, 0),
            'spawn': (0, 0, 255),
            'goal': (0, 255, 0),
            'text': (255, 255, 255),
            'button': (100, 100, 100),
            'hover': (150, 150, 150)
        }
        self.font = pygame.font.Font(None, 24)
        self.wall_start = None
        self.levels_folder = "levelsdata"
        os.makedirs(self.levels_folder, exist_ok=True)

    def run(self, screen, clock):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.save_level_menu(screen)
                    elif event.key == pygame.K_l:
                        self.load_level_menu(screen)

            self.draw(screen)
            pygame.display.flip()
            clock.tick(60)

    def handle_mouse_click(self, pos):
        x, y = pos
        if x > self.width:  # Clicked in the toolbar
            self.handle_toolbar_click(y)
        else:  # Clicked in the game area
            if self.current_tool == 'spawn':
                self.spawn = (x, y)
            elif self.current_tool == 'goal':
                self.goals.append((x, y))
            elif self.current_tool == 'wall':
                if self.wall_start is None:
                    self.wall_start = (x, y)
                else:
                    self.walls.append((self.wall_start[0], self.wall_start[1], x - self.wall_start[0], y - self.wall_start[1]))
                    self.wall_start = None

    def handle_toolbar_click(self, y):
        if y < 100:
            self.current_tool = 'spawn'
        elif y < 200:
            self.current_tool = 'goal'
        elif y < 300:
            self.current_tool = 'wall'

    def draw(self, screen):
        # Draw game area
        pygame.draw.rect(screen, self.colors['background'], (0, 0, self.width, self.height))
        
        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(screen, self.colors['wall'], wall)
        
        # Draw spawn point
        if self.spawn:
            pygame.draw.circle(screen, self.colors['spawn'], self.spawn, 5)
        
        # Draw goals
        for goal in self.goals:
            pygame.draw.circle(screen, self.colors['goal'], goal, 5)
        
        # Draw toolbar
        pygame.draw.rect(screen, (50, 50, 50), (self.width, 0, 200, self.height))
        self.draw_text(screen, "Spawn (S)", (self.width + 100, 50))
        self.draw_text(screen, "Goal (G)", (self.width + 100, 150))
        self.draw_text(screen, "Wall (W)", (self.width + 100, 250))
        self.draw_text(screen, f"Current: {self.current_tool}", (self.width + 100, 350))
        self.draw_text(screen, "Save (S)", (self.width + 100, 450))
        self.draw_text(screen, "Load (L)", (self.width + 100, 500))

    def draw_text(self, screen, text, pos):
        text_surface = self.font.render(text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=pos)
        screen.blit(text_surface, text_rect)

    def save_level_menu(self, screen):
        filename = self.text_input(screen, "Enter level name to save:")
        if filename:
            self.save_level(filename)

    def load_level_menu(self, screen):
        levels = self.get_available_levels()
        selected_level = self.selection_menu(screen, "Select a level to load:", levels)
        if selected_level:
            self.load_level(selected_level)

    def text_input(self, screen, prompt):
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

            screen.fill(self.colors['background'])
            self.draw_text(screen, prompt, (self.width // 2, self.height // 2 - 50))
            pygame.draw.rect(screen, self.colors['button'], (self.width // 2 - 100, self.height // 2, 200, 40))
            self.draw_text(screen, input_text, (self.width // 2, self.height // 2 + 20))
            pygame.display.flip()

        return input_text

    def selection_menu(self, screen, prompt, options):
        buttons = []
        button_height = 50
        button_width = 300
        start_y = 100
        max_buttons = 8
        scroll_offset = 0

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
                    elif event.button == 4:  # Scroll up
                        scroll_offset = max(0, scroll_offset - 1)
                    elif event.button == 5:  # Scroll down
                        scroll_offset = min(len(options) - max_buttons, scroll_offset + 1)

            screen.fill(self.colors['background'])
            self.draw_text(screen, prompt, (self.width // 2, 50))

            buttons = []
            for i, option in enumerate(options[scroll_offset:scroll_offset + max_buttons]):
                button = pygame.Rect(self.width // 2 - button_width // 2, start_y + i * (button_height + 10), button_width, button_height)
                buttons.append(button)
                mouse_pos = pygame.mouse.get_pos()
                color = self.colors['hover'] if button.collidepoint(mouse_pos) else self.colors['button']
                pygame.draw.rect(screen, color, button)
                self.draw_text(screen, option, button.center)

            # Draw scroll indicators
            if scroll_offset > 0:
                self.draw_text(screen, "↑", (self.width // 2, start_y - 20))
            if scroll_offset + max_buttons < len(options):
                self.draw_text(screen, "↓", (self.width // 2, start_y + max_buttons * (button_height + 10) + 20))

            pygame.display.flip()

    def get_available_levels(self):
        return [f for f in os.listdir(self.levels_folder) if f.endswith('.json')]

    def load_level(self, filename):
        filepath = os.path.join(self.levels_folder, filename)
        try:
            with open(filepath, 'r') as f:
                level_data = json.load(f)
            self.walls = level_data['walls']
            self.spawn = tuple(level_data['spawn'])
            self.goals = [tuple(goal) for goal in level_data['rewards']]
            print(f"Level loaded from {filepath}")
        except FileNotFoundError:
            print(f"Level file '{filepath}' not found")

    def save_level(self, filename):
        level_data = {
            'walls': self.walls,
            'spawn': self.spawn,
            'rewards': self.goals
        }
        filepath = os.path.join(self.levels_folder, f"{filename}.json")
        with open(filepath, 'w') as f:
            json.dump(level_data, f)
        print(f"Level saved to {filepath}")