import pygame
import numpy as np
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class PlayerEnv:
    def __init__(self):
        pygame.init()
        self.width, self.height = SCREEN_WIDTH, SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Dynamic Raycasting")
        self.clock = pygame.time.Clock()
        
        # Colors
        self.colors = {
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'green': (0, 255, 0),
            'yellow': (255, 255, 0),
            'purple': (128, 0, 128)
        }

        # Initialize player, walls, and goal
        self.player = self.Player(self.width // 2, self.height // 2)
        self.walls = []
        """[
            self.Wall(300, 300, 100, 100),
            self.Wall(500, 150, 150, 200)
        ]"""
        self.goal = self.Goal(700, 500, 25)
        self.raycast_intersections = []
        self.prev_distance = 0

    def close(self):
        """
        selfexplanatory
        """
        pygame.display.quit()
        pygame.quit()
        
    def reset(self):
        self.player = self.Player(self.width // 2+3, self.height // 2+3)
        self.raycast_intersections = []
        self.prev_distance = 0
        self.goal = self.Goal(random.randint(0, self.width), random.randint(0, self.height), 25)
        return self._get_obs()

    def step(self, action):
        pygame.event.pump()
        self.player.update(action)
        for wall in self.walls:
            if self.player.rect.colliderect(wall.rect):
                return self._get_obs(), -10.0, True

        if self._is_player_out_of_bounds():
            return self._get_obs(), -10.0, True
        
        win = self.goal.circle.colliderect(self.player.rect)
        distance = self._get_distance_to_goal()
        normalized_distance = distance / (SCREEN_WIDTH + SCREEN_HEIGHT) 
        if win:
            reward = 10.0
        else:
            if distance < self.prev_distance:
                reward = normalized_distance
            else:
                reward = -normalized_distance
            self.prev_distance = distance
        
        return self._get_obs(), reward, win

    def _get_distance_to_goal(self):
        player_center = self.player.rect.center
        goal_center = self.goal.circle.center
        distance = np.sqrt((player_center[0] - goal_center[0])**2 + (player_center[1] - goal_center[1])**2)
        return distance

    def render(self):
        self.screen.fill(self.colors['black'])
        self.player.draw(self.screen, self.colors['blue'])
        for wall in self.walls:
            wall.draw(self.screen, self.colors['red'])
        self.goal.draw(self.screen, self.colors['green'])

        center_of_screen = (self.width // 2, self.height // 2)
        start_pos = self.player.rect.center
        end_pos = center_of_screen
        color = self.colors['blue']

        for wall in self.walls:
            if self.get_line_intersection(start_pos, end_pos, (wall.rect.topleft, wall.rect.topright)) or \
               self.get_line_intersection(start_pos, end_pos, (wall.rect.topright, wall.rect.bottomright)) or \
               self.get_line_intersection(start_pos, end_pos, (wall.rect.bottomright, wall.rect.bottomleft)) or \
               self.get_line_intersection(start_pos, end_pos, (wall.rect.bottomleft, wall.rect.topleft)):
                color = self.colors['yellow']
                break

        pygame.draw.line(self.screen, color, start_pos, end_pos, 2)

        for start_pos, end_pos in self.raycast_intersections:
            pygame.draw.line(self.screen, self.colors['purple'], start_pos, end_pos, 2)

        pygame.display.flip()

    def _get_obs(self):
        player_x = self.player.rect.x / SCREEN_WIDTH
        player_y = self.player.rect.y / SCREEN_HEIGHT
        goal_x = self.goal.circle.center[0] / SCREEN_WIDTH
        goal_y = self.goal.circle.center[1] / SCREEN_HEIGHT
        return np.array([player_x, player_y, goal_x, goal_y])

    def _is_player_out_of_bounds(self):
        if self.player.rect.left <= 0 or self.player.rect.right >= self.width or \
           self.player.rect.top <= 0 or self.player.rect.bottom >= self.height:
            print("Player out of bounds")
            return True
        return False

    class Player:
        def __init__(self, x, y):
            self.rect = pygame.Rect(x+3, y+3, 50, 50)
            self.speed = 1

        def update(self, action):
            if action == 0:  # right
                self.rect.x += self.speed
            if action == 1:  # left
                self.rect.x -= self.speed
            if action == 2:  # up
                self.rect.y -= self.speed
            if action == 3:  # down
                self.rect.y += self.speed

            # Collision detection with screen boundaries
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT

        def draw(self, surface, color):
            pygame.draw.rect(surface, color, self.rect)

    class Wall:
        def __init__(self, x, y, width, height):
            self.rect = pygame.Rect(x, y, width, height)

        def draw(self, surface, color):
            pygame.draw.rect(surface, color, self.rect)

    class Goal:
        def __init__(self, x, y, radius):
            self.circle = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
            self.radius = radius

        def draw(self, surface, color):
            pygame.draw.circle(surface, color, self.circle.center, self.radius)

        def check_collision(self, player_rect):
            if self.circle.colliderect(player_rect):
                self.on_collision()

        def on_collision(self):
            print("You won!")

    def get_line_intersection(self, p1, p2, p3p4):
        """ Get the intersection point of two lines (p1 to p2 and p3 to p4) """
        p3, p4 = p3p4
        denom = (p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0])
        if denom == 0:
            return None

        px = ((p1[0] * p2[1] - p1[1] * p2[0]) * (p3[0] - p4[0]) - (p1[0] - p2[0]) * (p3[0] * p4[1] - p3[1] * p4[0])) / denom
        py = ((p1[0] * p2[1] - p1[1] * p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] * p4[1] - p3[1] * p4[0])) / denom

        if (min(p1[0], p2[0]) <= px <= max(p1[0], p2[0]) and
            min(p1[1], p2[1]) <= py <= max(p1[1], p2[1]) and
            min(p3[0], p4[0]) <= px <= max(p3[0], p4[0]) and
            min(p3[1], p4[1]) <= py <= max(p3[1], p4[1])):
            return (px, py)
        return None
    
    
