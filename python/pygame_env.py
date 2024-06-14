import pygame
import numpy as np
import random

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MIN_WALLS = 1
MAX_WALLS = 3
WITH_WALLS = True
WITH_BORDERS = True

class PlayerEnv:
    def __init__(self):
        pygame.init()
        self.width, self.height = SCREEN_WIDTH, SCREEN_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("AI Training Environment")
        self.clock = pygame.time.Clock()
        
        self.current_step = 0
        self.max_steps = 2500
        self.raycast_dist = 75

        self.prev_distances = []  
        self.stagnation_threshold = 10 
        self.stagnation_tolerance = 10
        
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
        self.goal = self.Goal(700, 500, 7)
        self.raycast_intersections = []
        self.prev_distance = 0

        # Initialize raycasts
        self.num_rays = 8
        self.ray_angles = np.linspace(0, 2 * np.pi, self.num_rays, endpoint=False)
        self.ray_distances = np.zeros(self.num_rays)

    def close(self):
        """
        selfexplanatory
        """
        pygame.display.quit()
        pygame.quit()
        
    def reset(self):
        self.current_step = 0
        for wall in self.walls:
            if self.player.rect.colliderect(wall.rect):
                self.player = self.Player(self.width // 2+3, self.height // 2+3)
        self.raycast_intersections = []
        self.prev_distance = 0

        self.walls = []

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

        center_x = self.width // 2
        center_y = self.height // 2
        offset = 200

        self.goal = self.Goal(random.randint(center_x - offset, center_x + offset), random.randint(center_y - offset, center_y + offset), 7)
        while self._is_goal_inside_wall():
            self.goal = self.Goal(random.randint(center_x - offset, center_x + offset), random.randint(center_y - offset, center_y + offset), 7)
        
        return self._get_obs()

    def step(self, action):
        pygame.event.pump()
        self.player.update(action)
        self.current_step += 1
        self._cast_rays()

        for wall in self.walls:
            if self.player.rect.colliderect(wall.rect):
                print("You hit a wall!")
                return self._get_obs(), -50.0, True  
        
        if self.current_step >= self.max_steps:
            return self._get_obs(), -75.0, True

        win = self.goal.circle.colliderect(self.player.rect)
        if win:
            #if max(self.ray_distances) > 0.0: 
            #    return self._get_obs(), 75.0, True  
            return self._get_obs(), 50.0, True 

        distance = self._get_distance_to_goal()
        normalized_distance = distance / (SCREEN_WIDTH + SCREEN_HEIGHT)

        reward = 0

        if len(self.prev_distances) >= self.stagnation_threshold:
            self.prev_distances.pop(0)
        self.prev_distances.append(distance)


        #if self.is_stuck():
        #    reward -= 0.5
            
        """if self.is_stuck():
            if distance > self.prev_distance:
                reward += 10.0  
            else:
                reward -= 0.5  
        else:
            if distance < self.prev_distance:
                reward += 0.1
            else:
                reward -= 0.05"""

        reward -= 0.1
        self.prev_distance = distance

        return self._get_obs(), reward, False

    def is_stuck(self):
        if len(self.prev_distances) < self.stagnation_threshold:
            return False
        min_distance = min(self.prev_distances)
        max_distance = max(self.prev_distances)
        return abs(max_distance - min_distance) < self.stagnation_tolerance

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
        end_pos = self.goal.circle.center
        color = self.colors['yellow']

        for wall in self.walls:
            if self.get_line_intersection(start_pos, end_pos, (wall.rect.topleft, wall.rect.topright)) or \
               self.get_line_intersection(start_pos, end_pos, (wall.rect.topright, wall.rect.bottomright)) or \
               self.get_line_intersection(start_pos, end_pos, (wall.rect.bottomright, wall.rect.bottomleft)) or \
               self.get_line_intersection(start_pos, end_pos, (wall.rect.bottomleft, wall.rect.topleft)):
                color = self.colors['yellow']
                break

        pygame.draw.line(self.screen, color, start_pos, end_pos, 2)

        for start_pos, end_pos in self.raycast_intersections:
            pygame.draw.circle(self.screen, self.colors['yellow'], end_pos, 5)

        # Draw raycasts
        for i, angle in enumerate(self.ray_angles):
            start_pos = self.player.rect.center
            end_pos = self._get_ray_end_pos(angle)
            pygame.draw.line(self.screen, self.colors['purple'], start_pos, end_pos, 1)

        pygame.display.flip()

    def _get_obs(self):
        player_x = self.player.rect.x 
        player_y = self.player.rect.y 
        goal_x = self.goal.circle.center[0] 
        goal_y = self.goal.circle.center[1] 
        
        player_to_goal_x = goal_x - player_x
        player_to_goal_y = goal_y - player_y
        
        distance = np.sqrt(player_to_goal_x**2 + player_to_goal_y**2)
        normalized_distance = distance / np.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)
        
        angle = np.arctan2(player_to_goal_y, player_to_goal_x)
        normalized_angle = (angle + np.pi) / (2 * np.pi)
        
        return np.concatenate(([normalized_angle, normalized_distance], self.ray_distances))

    def _is_player_out_of_bounds(self):
        if self.player.rect.left <= 0 or self.player.rect.right >= self.width or \
           self.player.rect.top <= 0 or self.player.rect.bottom >= self.height:
            return True
        return False

    def _cast_rays(self):
        self.raycast_intersections = []
        self.ray_distances = np.zeros(self.num_rays)

        for i, angle in enumerate(self.ray_angles):
            end_pos = self._get_ray_end_pos(angle)
            intersection = self._get_ray_intersection(end_pos)
            if intersection:
                self.raycast_intersections.append((self.player.rect.center, intersection))
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
            if self.get_line_intersection(self.player.rect.center, end_pos, (wall.rect.topleft, wall.rect.topright)) or \
               self.get_line_intersection(self.player.rect.center, end_pos, (wall.rect.topright, wall.rect.bottomright)) or \
               self.get_line_intersection(self.player.rect.center, end_pos, (wall.rect.bottomright, wall.rect.bottomleft)) or \
               self.get_line_intersection(self.player.rect.center, end_pos, (wall.rect.bottomleft, wall.rect.topleft)):
                return self.get_line_intersection(self.player.rect.center, end_pos, (wall.rect.topleft, wall.rect.topright)) or \
                       self.get_line_intersection(self.player.rect.center, end_pos, (wall.rect.topright, wall.rect.bottomright)) or \
                       self.get_line_intersection(self.player.rect.center, end_pos, (wall.rect.bottomright, wall.rect.bottomleft)) or \
                       self.get_line_intersection(self.player.rect.center, end_pos, (wall.rect.bottomleft, wall.rect.topleft))
        return None

    def _get_distance(self, p1, p2):
        return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def _is_goal_inside_wall(self):
        for wall in self.walls:
            if wall.rect.colliderect(self.goal.circle):
                return True
        return False

    class Player:
        def __init__(self, x, y):
            self.rect = pygame.Rect(x+3, y+3, 10, 10)
            self.speed = 4

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
    
    
