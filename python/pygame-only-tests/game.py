import pygame
import numpy as np
import random
import sys

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MIN_WALLS = 1
MAX_WALLS = 3
WITH_WALLS = True
WITH_BORDERS = True

class Game:
    def __init__(self):
        self.width, self.height = SCREEN_WIDTH, SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AI Training Environment")
        self.clock = pygame.time.Clock()

        self.colors = {
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'yellow': (255, 255, 0),
            'purple': (128, 0, 128),
            'white': (255, 255, 255),
            'gray': (200, 200, 200)
        }
        self.player = None
        self.walls = []
        self.goals = []
        self.raycast_dist = 75
        self.num_rays = 8
        self.ray_angles = np.linspace(0, 2 * np.pi, self.num_rays, endpoint=False)
        self.ray_distances = np.zeros(self.num_rays)

        self.levels = {
            'level1': {
                'walls': [
                    (100, 100, 10, 200),
                    (300, 300, 200, 10),
                ],
                'spawn': (50, 50),
                'rewards': [(700, 500)],
            },
            'level2': {
                'walls': [
                    (200, 100, 10, 400),
                    (400, 100, 10, 400),
                ],
                'spawn': (100, 100),
                'rewards': [(600, 300), (700, 500)],
            },
        }
        self.current_level = None
        self.font = pygame.font.Font(None, 36)

    # Menu logic
    def draw_text(self, text, font, color, surface, x, y):
        textobj = font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)

    def main_menu(self):
        while True:
            pygame.display.flip()
            self.screen.fill(self.colors['black'])
            self.draw_text('Main Menu', self.font, self.colors['white'], self.screen, 20, 20)

            mx, my = pygame.mouse.get_pos()

            button_1 = pygame.Rect(50, 100, 200, 50)
            button_2 = pygame.Rect(50, 200, 200, 50)
            
            pygame.draw.rect(self.screen, self.colors['gray'], button_1)
            pygame.draw.rect(self.screen, self.colors['gray'], button_2)

            self.draw_text('Level 1', self.font, self.colors['black'], self.screen, 60, 110)
            self.draw_text('Level 2', self.font, self.colors['black'], self.screen, 60, 210)

            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True

            if button_1.collidepoint((mx, my)):
                if click:
                    return self.level_menu('level1')
            if button_2.collidepoint((mx, my)):
                if click:
                    return self.level_menu('level2')

            pygame.display.update()
            self.clock.tick(60)

    def level_menu(self, level):
        while True:
            self.screen.fill(self.colors['black'])
            self.draw_text(f'Level {level[-1]} Menu', self.font, self.colors['white'], self.screen, 20, 20)

            mx, my = pygame.mouse.get_pos()

            button_1 = pygame.Rect(50, 100, 200, 50)
            button_2 = pygame.Rect(50, 200, 200, 50)
            button_3 = pygame.Rect(50, 300, 200, 50)
            
            pygame.draw.rect(self.screen, self.colors['gray'], button_1)
            pygame.draw.rect(self.screen, self.colors['gray'], button_2)
            pygame.draw.rect(self.screen, self.colors['gray'], button_3)

            self.draw_text('Player Mode', self.font, self.colors['black'], self.screen, 60, 110)
            self.draw_text('AI Mode', self.font, self.colors['black'], self.screen, 60, 210)
            self.draw_text('Back', self.font, self.colors['black'], self.screen, 60, 310)

            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True

            if button_1.collidepoint((mx, my)):
                if click:
                    return level, 'player'
            if button_2.collidepoint((mx, my)):
                if click:
                    return level, 'ai'
            if button_3.collidepoint((mx, my)):
                if click:
                    self.main_menu()

            pygame.display.update()
            self.clock.tick(60)

    def game_over_menu(self, score):
        while True:
            self.screen.fill(self.colors['black'])
            self.draw_text('Game Over', self.font, self.colors['white'], self.screen, 20, 20)
            self.draw_text(f'Score: {score}', self.font, self.colors['white'], self.screen, 20, 60)

            mx, my = pygame.mouse.get_pos()

            button_1 = pygame.Rect(50, 100, 200, 50)
            button_2 = pygame.Rect(50, 200, 200, 50)
            
            pygame.draw.rect(self.screen, self.colors['gray'], button_1)
            pygame.draw.rect(self.screen, self.colors['gray'], button_2)

            self.draw_text('Play Again', self.font, self.colors['black'], self.screen, 60, 110)
            self.draw_text('Main Menu', self.font, self.colors['black'], self.screen, 60, 210)

            click = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True

            if button_1.collidepoint((mx, my)):
                if click:
                    return 'play_again'
            if button_2.collidepoint((mx, my)):
                if click:
                    return 'main_menu'

            pygame.display.update()
            self.clock.tick(60)

    def set_level(self, level_name):
        if level_name in self.levels:
            self.current_level = self.levels[level_name]
            self.reset()
        else:
            raise ValueError(f"Level '{level_name}' not found")

    def reset(self):
        if self.current_level:
            self.player = self.Player(*self.current_level['spawn'])
            self.walls = [self.Wall(*wall) for wall in self.current_level['walls']]
            self.goals = [self.Goal(*reward, 7) for reward in self.current_level['rewards']]
        else:
            self.player = self.Player(self.width // 2, self.height // 2)
            self.walls = []
            self.goals = [self.Goal(700, 500, 7)]

        self._setup_walls()
        return self._get_state(), 0, False

    def _setup_walls(self):
        if WITH_BORDERS:
            for x in range(0, self.width, 50):
                self.walls.append(self.Wall(x, 0, 50, 10))
                self.walls.append(self.Wall(x, self.height - 10, 50, 10))
            for y in range(10, self.height - 10, 50):
                self.walls.append(self.Wall(0, y, 10, 50))
                self.walls.append(self.Wall(self.width - 10, y, 10, 50))

        if WITH_WALLS:
            for _ in range(random.randint(MIN_WALLS, MAX_WALLS)):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)
                width = random.randint(1, 10)
                height = random.randint(50, 200)
                if random.choice([True, False]):
                    self.walls.append(self.Wall(x, y, width, height))
                else:
                    self.walls.append(self.Wall(x, y, height, width))

    def step(self, action):
        self.player.update(action)
        self._cast_rays()

        for wall in self.walls:
            if self.player.rect.colliderect(wall.rect):
                return self._get_state(), -50.0, True

        for goal in self.goals:
            if goal.circle.colliderect(self.player.rect):
                self.goals.remove(goal)
                if not self.goals:
                    return self._get_state(), 50.0, True
                else:
                    return self._get_state(), 25.0, False

        return self._get_state(), -0.1, False

    def _get_state(self):
        player_x, player_y = self.player.rect.center
        goal_x, goal_y = self.goals[0].circle.center if self.goals else (0, 0)
        
        player_to_goal_x = goal_x - player_x
        player_to_goal_y = goal_y - player_y
        
        distance = np.sqrt(player_to_goal_x**2 + player_to_goal_y**2)
        normalized_distance = distance / np.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)
        
        angle = np.arctan2(player_to_goal_y, player_to_goal_x)
        normalized_angle = (angle + np.pi) / (2 * np.pi)
        
        return np.concatenate(([normalized_angle, normalized_distance], self.ray_distances))

    def _cast_rays(self):
        self.ray_distances = np.zeros(self.num_rays)
        for i, angle in enumerate(self.ray_angles):
            end_pos = self._get_ray_end_pos(angle)
            intersection = self._get_ray_intersection(end_pos)
            if intersection:
                ray_length = self._get_distance(self.player.rect.center, intersection)
                normalized_distance = 1 - (ray_length / self.raycast_dist)
                self.ray_distances[i] = normalized_distance

    def _get_ray_end_pos(self, angle):
        dx = np.cos(angle)
        dy = np.sin(angle)
        end_pos = (self.player.rect.center[0] + dx * self.raycast_dist, self.player.rect.center[1] + dy * self.raycast_dist)
        return end_pos

    def _get_ray_intersection(self, end_pos):
        for wall in self.walls:
            intersection = self._get_line_intersection(self.player.rect.center, end_pos, wall.rect)
            if intersection:
                return intersection
        return None

    def _get_line_intersection(self, p1, p2, rect):
        lines = [
            (rect.topleft, rect.topright),
            (rect.topright, rect.bottomright),
            (rect.bottomright, rect.bottomleft),
            (rect.bottomleft, rect.topleft)
        ]
        for line in lines:
            intersection = self._get_line_segment_intersection(p1, p2, *line)
            if intersection:
                return intersection
        return None

    def _get_line_segment_intersection(self, p1, p2, p3, p4):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        
        denom = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
        if denom == 0:
            return None
        ua = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / denom
        if ua < 0 or ua > 1:
            return None
        ub = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / denom
        if ub < 0 or ub > 1:
            return None
        x = x1 + ua * (x2-x1)
        y = y1 + ua * (y2-y1)
        return (x, y)

    def _get_distance(self, p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def render(self):
        self.screen.fill(self.colors['black'])
        pygame.draw.rect(self.screen, self.colors['blue'], self.player.rect)
        for wall in self.walls:
            pygame.draw.rect(self.screen, self.colors['red'], wall.rect)
        for goal in self.goals:
            pygame.draw.circle(self.screen, self.colors['green'], goal.circle.center, goal.radius)

        # Draw raycasts
        for i, angle in enumerate(self.ray_angles):
            start_pos = self.player.rect.center
            end_pos = self._get_ray_end_pos(angle)
            pygame.draw.line(self.screen, self.colors['purple'], start_pos, end_pos, 1)

        pygame.display.flip()
        self.clock.tick(60)

    class Player:
        def __init__(self, x, y):
            self.rect = pygame.Rect(x+3, y+3, 10, 10)
            self.speed = 4

        def update(self, action):
            if action == 0:  # right
                self.rect.x += self.speed
            elif action == 1:  # left
                self.rect.x -= self.speed
            elif action == 2:  # up
                self.rect.y -= self.speed
            elif action == 3:  # down
                self.rect.y += self.speed

            # Collision detection with screen boundaries
            self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    class Wall:
        def __init__(self, x, y, width, height):
            self.rect = pygame.Rect(x, y, width, height)

    class Goal:
        def __init__(self, x, y, radius):
            self.circle = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
            self.radius = radius