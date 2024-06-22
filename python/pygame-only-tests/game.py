import pygame
import numpy as np
import random
import os
import json

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MIN_WALLS = 1
MAX_WALLS = 3
WITH_BORDERS = True

class Game:
    def __init__(self):
        self.width, self.height = SCREEN_WIDTH, SCREEN_HEIGHT
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
        self.ray_endpoints = [None] * self.num_rays

        self.levels_folder = "levelsdata"
        self.levels = self.load_all_levels()
        self.current_level = None

    def set_level(self, level_name):
        if level_name in self.levels:
            self.current_level = self.levels[level_name]
            self.reset()
        else:
            raise ValueError(f"Level '{level_name}' not found")

    def load_level_from_json(self, filename):
        try:
            with open(filename, 'r') as f:
                self.current_level = json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Level file '{filename}' not found")

    def save_level_to_json(self, filename):
        level_data = {
            'walls': [wall.rect for wall in self.walls],
            'spawn': self.player.rect.topleft,
            'rewards': [goal.circle.center for goal in self.goals]
        }
        with open(filename, 'w') as f:
            json.dump(level_data, f)

    def load_all_levels(self):
        levels = {}
        for filename in os.listdir(self.levels_folder):
            if filename.endswith('.json'):
                level_name = os.path.splitext(filename)[0]
                filepath = os.path.join(self.levels_folder, filename)
                with open(filepath, 'r') as f:
                    levels[level_name] = json.load(f)
        return levels

    def reset(self):
        if self.current_level:
            self.player = Player(*self.current_level['spawn'])
            self.walls = [Wall(*wall) for wall in self.current_level['walls']]
            self.goals = [Goal(*reward, 7) for reward in self.current_level['rewards']]
        else:
            self.player = Player(self.width // 2, self.height // 2)
            self.walls = []
            self.goals = [Goal(700, 500, 7)]
        if WITH_BORDERS:
            self._setup_borders()
        return self._get_state(), 0, False

    def _setup_borders(self):
        for x in range(0, self.width, 50):
            self.walls.append(Wall(x, 0, 50, 10))
            self.walls.append(Wall(x, self.height - 10, 50, 10))
        for y in range(10, self.height - 10, 50):
            self.walls.append(Wall(0, y, 10, 50))
            self.walls.append(Wall(self.width - 10, y, 10, 50))


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
        self.ray_endpoints = [None] * self.num_rays
        for i, angle in enumerate(self.ray_angles):
            end_pos = self._get_ray_end_pos(angle)
            intersection = self._get_ray_intersection(end_pos)
            if intersection:
                ray_length = self._get_distance(self.player.rect.center, intersection)
                normalized_distance = 1 - (ray_length / self.raycast_dist)
                self.ray_distances[i] = normalized_distance
                self.ray_endpoints[i] = intersection
            else:
                self.ray_endpoints[i] = end_pos

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

    def render(self, surface):
            surface.fill(self.colors['black'])
            pygame.draw.rect(surface, self.colors['blue'], self.player.rect)
            for wall in self.walls:
                pygame.draw.rect(surface, self.colors['red'], wall.rect)
            for goal in self.goals:
                pygame.draw.circle(surface, self.colors['green'], goal.circle.center, goal.radius)

            # Draw raycasts
            for i, end_point in enumerate(self.ray_endpoints):
                if end_point:
                    pygame.draw.line(surface, self.colors['yellow'], self.player.rect.center, end_point)
                    if self.ray_distances[i] > 0:
                        pygame.draw.circle(surface, self.colors['purple'], end_point, 3)

            # Draw line to objective
            if self.goals:
                goal = self.goals[0]
                pygame.draw.line(surface, self.colors['white'], self.player.rect.center, goal.circle.center)
                midpoint = ((self.player.rect.centerx + goal.circle.centerx) // 2,
                            (self.player.rect.centery + goal.circle.centery) // 2)
                distance = self._get_distance(self.player.rect.center, goal.circle.center)
                angle = np.arctan2(goal.circle.centery - self.player.rect.centery,
                                   goal.circle.centerx - self.player.rect.centerx)
                angle_deg = np.degrees(angle)
                font = pygame.font.Font(None, 24)
                text = font.render(f"{distance:.1f}px, {angle_deg:.1f}°", True, self.colors['white'])
                surface.blit(text, midpoint)

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