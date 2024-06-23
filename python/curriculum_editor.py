import pygame
import json
from typing import List, Dict
import os

class CurriculumStep:
    def __init__(self, episodes: int, levels: Dict[str, float]):
        self.episodes = episodes
        self.levels = levels

class Curriculum:
    def __init__(self):
        self.steps: List[CurriculumStep] = []

    def add_step(self, step: CurriculumStep):
        self.steps.append(step)

    def remove_step(self, index: int):
        if 0 <= index < len(self.steps):
            del self.steps[index]

    def save_to_json(self, filename: str):
        data = [{"episodes": step.episodes, "levels": step.levels} for step in self.steps]
        with open(filename, 'w') as f:
            json.dump(data, f)

    @classmethod
    def load_from_json(cls, filename: str):
        curriculum = cls()
        with open(filename, 'r') as f:
            data = json.load(f)
        for step_data in data:
            curriculum.add_step(CurriculumStep(step_data["episodes"], step_data["levels"]))
        return curriculum

class CurriculumEditor:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.curriculum = Curriculum()
        self.font = pygame.font.Font(None, 24)
        self.input_font = pygame.font.Font(None, 32)
        self.colors = {
            'background': (0, 0, 0),
            'text': (255, 255, 255),
            'button': (100, 100, 100),
            'button_hover': (150, 150, 150),
            'button_text': (255, 255, 255),
            'remove': (255, 0, 0),
            'add': (0, 255, 0),
        }
        self.available_levels = ["corridor-h1", "corridor-h2", "corridor-v1", "corridor-v2", "reward-zone-all", "reward-zone1"]
        self.scroll_offset = 0
        self.step_width = 300
        self.step_height = 250
        self.step_spacing = 20
        self.selected_level = None

    def run(self, screen):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)

            self.draw(screen)
            pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self.handle_click(event.pos)
            elif event.button == 4:  # Scroll left
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:  # Scroll right
                max_scroll = max(0, len(self.curriculum.steps) - (self.screen_width - 100) // (self.step_width + self.step_spacing))
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.key == pygame.K_RIGHT:
                max_scroll = max(0, len(self.curriculum.steps) - (self.screen_width - 100) // (self.step_width + self.step_spacing))
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)

    def handle_click(self, pos):
        x, y = pos

        # Check if clicked on a step
        for i, step in enumerate(self.curriculum.steps[self.scroll_offset:]):
            step_x = 50 + i * (self.step_width + self.step_spacing) - self.scroll_offset * (self.step_width + self.step_spacing)
            if step_x <= x < step_x + self.step_width and 50 <= y < 50 + self.step_height:
                self.handle_step_click(i + self.scroll_offset, x - step_x, y - 50)
                return

        # Check if clicked on available levels
        for i, level in enumerate(self.available_levels):
            button = pygame.Rect(10, 50 + i * 60, 180, 50)
            if button.collidepoint(pos):
                self.selected_level = level
                return

        # Check if clicked on bottom buttons
        buttons = [
            ("Add Step", (self.screen_width - 220, self.screen_height - 60, 200, 40)),
            ("Save Curriculum", (self.screen_width - 440, self.screen_height - 60, 200, 40)),
            ("Load Curriculum", (self.screen_width - 660, self.screen_height - 60, 200, 40)),
            ("Back", (20, self.screen_height - 60, 180, 40))
        ]
        for text, rect in buttons:
            if pygame.Rect(rect).collidepoint(pos):
                if text == "Add Step":
                    self.add_step()
                elif text == "Save Curriculum":
                    self.save_curriculum()
                elif text == "Load Curriculum":
                    self.load_curriculum()
                elif text == "Back":
                    return False  # Exit the curriculum editor
                return

    def handle_step_click(self, step_index, rel_x, rel_y):
        step = self.curriculum.steps[step_index]

        # Check if clicked on remove step button
        if 250 <= rel_x <= 280 and 10 <= rel_y <= 40:
            self.curriculum.remove_step(step_index)
            return

        # Check if clicked on episodes input
        if 120 <= rel_x <= 180 and 40 <= rel_y <= 70:
            new_episodes = self.get_number_input("Enter number of episodes:", step.episodes)
            if new_episodes is not None:
                step.episodes = int(new_episodes)
            return

        # Check if clicked on level percentages
        for i, (level, percentage) in enumerate(step.levels.items()):
            if 10 <= rel_x <= 240 and 80 + i * 30 <= rel_y <= 110 + i * 30:
                new_percentage = self.get_number_input(f"Enter percentage for {level}:", percentage)
                if new_percentage is not None:
                    step.levels[level] = new_percentage
                return

        # Check if clicked on add level button
        if 10 <= rel_x <= 40 and self.step_height - 40 <= rel_y <= self.step_height - 10:
            if self.selected_level and self.selected_level not in step.levels:
                step.levels[self.selected_level] = 0
            return

        # Check if clicked on remove level button
        if 50 <= rel_x <= 80 and self.step_height - 40 <= rel_y <= self.step_height - 10:
            if self.selected_level and self.selected_level in step.levels:
                del step.levels[self.selected_level]
            return

        # Check if clicked on edit episodes button
        if 220 <= rel_x <= 250 and 40 <= rel_y <= 60:  # Updated coordinates
            new_episodes = self.get_number_input("Enter number of episodes:", step.episodes)
            if new_episodes is not None:
                step.episodes = int(new_episodes)
            return


        # Check if clicked on edit percentage buttons
        for i, (level, percentage) in enumerate(step.levels.items()):
            if 245 <= rel_x <= 275 and 80 + i * 30 <= rel_y <= 110 + i * 30:
                new_percentage = self.get_number_input(f"Enter percentage for {level}:", percentage)
                if new_percentage is not None:
                    step.levels[level] = new_percentage
                return

    def add_step(self):
        new_step = CurriculumStep(50, {level: 50 for level in self.available_levels[:2]})
        self.curriculum.add_step(new_step)

    def get_number_input(self, prompt, initial_value=None):
        input_text = str(initial_value) if initial_value is not None else ""
        input_active = True
        input_rect = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 - 16, 200, 32)

        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        try:
                            return float(input_text)
                        except ValueError:
                            # If the input is not a valid number, don't close the input box
                            continue
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isnumeric() or event.unicode == '.':
                        input_text += event.unicode

            screen = pygame.display.get_surface()
            screen.fill(self.colors['background'])

            # Draw prompt
            self.draw_text(screen, prompt, (self.screen_width // 2, self.screen_height // 2 - 50))

            # Draw input box
            pygame.draw.rect(screen, self.colors['button'], input_rect)
            text_surface = self.input_font.render(input_text, True, self.colors['text'])
            screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

            # Draw error message if input is invalid
            try:
                float(input_text)
            except ValueError:
                if input_text:
                    error_text = "Invalid number. Please enter a valid number."
                    error_surface = self.font.render(error_text, True, (255, 0, 0))
                    screen.blit(error_surface, (self.screen_width // 2 - 100, self.screen_height // 2 + 20))

            pygame.display.flip()

        return None

    def draw(self, screen):
        screen.fill(self.colors['background'])
        self.draw_steps(screen)
        self.draw_available_levels(screen)
        self.draw_buttons(screen)

    def draw_steps(self, screen):
        for i, step in enumerate(self.curriculum.steps):
            x_offset = 160 + i * (self.step_width + self.step_spacing) - self.scroll_offset * (self.step_width + self.step_spacing)
            if -self.step_width < x_offset < self.screen_width:
                pygame.draw.rect(screen, self.colors['button'], (50 + x_offset, 50, self.step_width, self.step_height))
                self.draw_text(screen, f"Step {i + 1}", (x_offset + self.step_width//2 + 50, 70))
                self.draw_text(screen, f"Episodes: {step.episodes}", (x_offset + self.step_width//2 + 50, 100))

                # Draw edit button for episodes
                edit_episodes_button = pygame.Rect(270 + x_offset, 90, 30, 20)
                pygame.draw.rect(screen, self.colors['button_hover'], edit_episodes_button)
                self.draw_text(screen, "Edit", edit_episodes_button.center, font_size=16)

                for j, (level, probability) in enumerate(step.levels.items()):
                    self.draw_text(screen, f"{level}: {probability}%", (x_offset + self.step_width//2 + 50, 130 + j * 30))

                    # Draw edit button for each level percentage
                    edit_percentage_button = pygame.Rect(295 + x_offset, 120 + j * 30, 30, 20)
                    pygame.draw.rect(screen, self.colors['button_hover'], edit_percentage_button)
                    self.draw_text(screen, "Edit", edit_percentage_button.center, font_size=16)

                remove_button = pygame.Rect(300 + x_offset, 60, 30, 30)
                pygame.draw.rect(screen, self.colors['remove'], remove_button)
                self.draw_text(screen, "X", remove_button.center)

                add_level_button = pygame.Rect(60 + x_offset, self.step_height + 10, 30, 30)
                pygame.draw.rect(screen, self.colors['add'], add_level_button)
                self.draw_text(screen, "+", add_level_button.center)

                remove_level_button = pygame.Rect(100 + x_offset, self.step_height + 10, 30, 30)
                pygame.draw.rect(screen, self.colors['remove'], remove_level_button)
                self.draw_text(screen, "-", remove_level_button.center)

    def draw_available_levels(self, screen):
        for i, level in enumerate(self.available_levels):
            button = pygame.Rect(10, 50 + i * 60, 180, 50)
            color = self.colors['button_hover'] if level == self.selected_level else self.colors['button']
            pygame.draw.rect(screen, color, button)
            self.draw_text(screen, level, button.center)

    def draw_buttons(self, screen):
        buttons = [
            ("Add Step", (self.screen_width - 220, self.screen_height - 60, 200, 40)),
            ("Save Curriculum", (self.screen_width - 440, self.screen_height - 60, 200, 40)),
            ("Load Curriculum", (self.screen_width - 660, self.screen_height - 60, 200, 40)),
            ("Back", (20, self.screen_height - 60, 180, 40))
        ]

        for text, rect in buttons:
            pygame.draw.rect(screen, self.colors['button'], rect)
            self.draw_text(screen, text, (rect[0] + rect[2] // 2, rect[1] + rect[3] // 2))

    def draw_text(self, screen, text, position, color=None, font_size=24):
        if color is None:
            color = self.colors['text']
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=position)
        screen.blit(text_surface, text_rect)

    def save_curriculum(self):
        filename = self.get_text_input("Enter filename to save:")
        if filename:
            # Create the 'curriculadata' folder if it doesn't exist
            os.makedirs('curriculadata', exist_ok=True)
            
            # Save the file in the 'curriculadata' folder
            filepath = os.path.join('curriculadata', f"{filename}.json")
            self.curriculum.save_to_json(filepath)
            print(f"Curriculum saved to {filepath}")

    def load_curriculum(self):
        filename = self.get_text_input("Enter filename to load:")
        if filename:
            # Construct the full file path
            filepath = os.path.join('curriculadata', f"{filename}.json")
            try:
                # Attempt to load the curriculum from the file
                self.curriculum = Curriculum.load_from_json(filepath)
                print(f"Curriculum successfully loaded from {filepath}")
            except FileNotFoundError:
                print(f"Error: File '{filepath}' not found.")
            except json.JSONDecodeError:
                print(f"Error: '{filepath}' is not a valid JSON file.")
            except Exception as e:
                print(f"An unexpected error occurred while loading the curriculum: {str(e)}")

    def get_text_input(self, prompt):
        input_text = ""
        input_active = True

        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return input_text
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

            screen = pygame.display.get_surface()
            screen.fill(self.colors['background'])

            # Draw prompt
            self.draw_text(screen, prompt, (self.screen_width // 2, self.screen_height // 2 - 50))

            # Draw input box
            pygame.draw.rect(screen, self.colors['button'], (self.screen_width // 2 - 100, self.screen_height // 2, 200, 40))
            text_surface = self.font.render(input_text, True, self.colors['text'])
            screen.blit(text_surface, (self.screen_width // 2 - 95, self.screen_height // 2 + 5))

            pygame.display.flip()

def curriculum_editor_mode(screen, font, game, clock):
    editor = CurriculumEditor(screen.get_width(), screen.get_height())
    editor.run(screen)