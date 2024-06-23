import pygame
import json
import os

class LevelEditor:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.toolbar_width = 200
        self.walls = []
        self.spawn = None
        self.goals = []
        self.reward_zones = []
        self.current_reward_zone = None
        self.current_tool = 'spawn'
        self.colors = {
            'background': (0, 0, 0),
            'wall': (255, 0, 0),
            'wall_preview': (255, 100, 100),
            'spawn': (0, 0, 255),
            'goal': (0, 255, 0),
            'text': (255, 255, 255),
            'button': (100, 100, 100),
            'hover': (150, 150, 150),
            'eraser': (255, 255, 0),
            'toolbar': (50, 50, 50),
            'reward_zone': (0, 255, 0, 128),
        }
        self.font = pygame.font.Font(None, 24)
        self.wall_start = None
        self.levels_folder = "levelsdata"
        os.makedirs(self.levels_folder, exist_ok=True)
        self.eraser_size = 10
        self.back_button = pygame.Rect(10, self.height - 60, 180, 40)


    def run(self, screen, clock):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.back_button.collidepoint(event.pos):
                        return  # Exit the level editor
                    else:
                        self.handle_mouse_click(event.pos)
                elif event.type == pygame.MOUSEMOTION:
                    if event.buttons[0]:  # Left mouse button held down
                        self.handle_mouse_drag(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.save_level_menu(screen)
                    elif event.key == pygame.K_l:
                        self.load_level_menu(screen)

            self.draw(screen)
            pygame.display.flip()
            clock.tick(60)

    def draw(self, screen):
        # Draw game area
        pygame.draw.rect(screen, self.colors['background'], (0, 0, self.width, self.height))

        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(screen, self.colors['wall'], wall)

        # Draw wall preview
        if self.wall_start is not None:
            end_pos = pygame.mouse.get_pos()
            x1, y1 = self.wall_start
            x2, y2 = end_pos
            x = min(x1, x2)
            y = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            pygame.draw.rect(screen, self.colors['wall_preview'], (x, y, width, height), 2)

        # Draw spawn point
        if self.spawn:
            pygame.draw.circle(screen, self.colors['spawn'], self.spawn, 5)

        # Draw goals
        for goal in self.goals:
            pygame.draw.circle(screen, self.colors['goal'], goal, 5)

        for zone in self.reward_zones:
            pygame.draw.circle(screen, self.colors['reward_zone'], zone['center'], zone['radius'], 2)

        # Draw reward zone preview
        if self.current_reward_zone:
            center = self.current_reward_zone['center']
            end_pos = pygame.mouse.get_pos()
            radius = int(((center[0] - end_pos[0])**2 + (center[1] - end_pos[1])**2)**0.5)
            pygame.draw.circle(screen, self.colors['reward_zone'], center, radius, 2)

        # Draw toolbar (clear it first)
        pygame.draw.rect(screen, self.colors['toolbar'], (self.width, 0, self.toolbar_width, self.height))

        # Draw toolbar buttons
        button_height = 50
        button_spacing = 10
        buttons = [
            ("Spawn", 'spawn'),
            ("Goal", 'goal'),
            ("Wall", 'wall'),
            ("Eraser", 'eraser'),
            ("Reward zone", 'reward_zone'),
            ("Clear All", 'clear'),
            (f"Current: {self.current_tool}", None),
            ("Save (S)", 'save'),
            ("Load (L)", 'load')
        ]

        for i, (text, tool) in enumerate(buttons):
            button_y = i * (button_height + button_spacing)
            button_rect = pygame.Rect(self.width + 10, button_y + 10, self.toolbar_width - 20, button_height)

            if tool == self.current_tool:
                pygame.draw.rect(screen, self.colors['hover'], button_rect)
            else:
                pygame.draw.rect(screen, self.colors['button'], button_rect)

            self.draw_text(screen, text, (button_rect.centerx, button_rect.centery))

        # Draw eraser preview if eraser tool is selected
        if self.current_tool == 'eraser':
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < self.width:  # Only draw in game area
                pygame.draw.rect(screen, self.colors['eraser'],
                                (mouse_pos[0] - self.eraser_size // 2,
                                mouse_pos[1] - self.eraser_size // 2,
                                self.eraser_size, self.eraser_size), 2)

        # Draw back button
        pygame.draw.rect(screen, self.colors['button'], self.back_button)
        self.draw_text(screen, "Back", self.back_button.center)

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
                    self.finish_wall((x, y))
            elif self.current_tool == 'eraser':
                self.erase(x, y)
            elif self.current_tool == 'reward_zone':
                if self.current_reward_zone is None:
                    self.current_reward_zone = {'center': (x, y)}
                else:
                    end_pos = (x, y)
                    radius = int(((self.current_reward_zone['center'][0] - end_pos[0])**2 +
                                  (self.current_reward_zone['center'][1] - end_pos[1])**2)**0.5)
                    self.current_reward_zone['radius'] = radius
                    self.reward_zones.append(self.current_reward_zone)
                    self.current_reward_zone = None

    def handle_mouse_drag(self, pos):
        if self.current_tool == 'eraser':
            self.erase(pos[0], pos[1])

    def handle_toolbar_click(self, y):
        button_height = 50
        button_spacing = 10
        total_button_height = button_height + button_spacing

        button_index = y // total_button_height

        if button_index == 0:
            self.current_tool = 'spawn'
        elif button_index == 1:
            self.current_tool = 'goal'
        elif button_index == 2:
            self.current_tool = 'wall'
        elif button_index == 3:
            self.current_tool = 'eraser'
        elif button_index == 4:
            self.current_tool = 'reward_zone'
        elif button_index == 5:
            self.clear_level()
        # Ignore the "Current: tool" button
        elif button_index == 6:
            self.save_level_menu(pygame.display.get_surface())
        elif button_index == 7:
            self.load_level_menu(pygame.display.get_surface())

    def erase(self, x, y):
        eraser_rect = pygame.Rect(x - self.eraser_size // 2, y - self.eraser_size // 2,
                                  self.eraser_size, self.eraser_size)
        self.walls = [wall for wall in self.walls if not eraser_rect.colliderect(wall)]
        self.goals = [goal for goal in self.goals if not eraser_rect.collidepoint(goal)]
        if self.spawn and eraser_rect.collidepoint(self.spawn):
            self.spawn = None

    def finish_wall(self, end_pos):
        if self.wall_start is not None:
            x1, y1 = self.wall_start
            x2, y2 = end_pos
            x = min(x1, x2)
            y = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            if width > 0 and height > 0:
                self.walls.append(pygame.Rect(x, y, width, height))
            self.wall_start = None

    def clear_level(self):
        self.walls = []
        self.spawn = None
        self.goals = []
        self.reward_zones = []

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
                        if self.back_button.collidepoint(mouse_pos):
                            return None
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

            # Draw back button
            pygame.draw.rect(screen, self.colors['button'], self.back_button)
            self.draw_text(screen, "Back", self.back_button.center)

            pygame.display.flip()

    def get_available_levels(self):
        return [f for f in os.listdir(self.levels_folder) if f.endswith('.json')]

    def load_level(self, filename):
        filepath = os.path.join(self.levels_folder, filename)
        try:
            with open(filepath, 'r') as f:
                level_data = json.load(f)
            self.walls = [pygame.Rect(*wall) for wall in level_data['walls']]
            self.spawn = tuple(level_data['spawn'])
            self.goals = [tuple(goal) for goal in level_data['rewards']]
            self.reward_zones = level_data.get('reward_zones', [])
            print(f"Level loaded from {filepath}")
        except FileNotFoundError:
            print(f"Level file '{filepath}' not found")

    def save_level(self, filename):
        level_data = {
            'walls': [(wall.x, wall.y, wall.width, wall.height) for wall in self.walls],
            'spawn': self.spawn,
            'rewards': self.goals,
            'reward_zones': self.reward_zones
        }
        filepath = os.path.join(self.levels_folder, f"{filename}.json")
        with open(filepath, 'w') as f:
            json.dump(level_data, f)
        print(f"Level saved to {filepath}")