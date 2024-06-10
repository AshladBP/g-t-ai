import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Dynamic Raycasting")

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Clock object to manage frame rate
clock = pygame.time.Clock()

# Control whether spacebar is required to advance a step
require_space_to_advance = True

# Variable to store the raycast intersections
raycast_intersections = []

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 20

    def update(self):
        keys = pygame.key.get_pressed()
        self.velocity = pygame.Vector2(0, 0)
        if keys[pygame.K_RIGHT]:
            self.velocity.x += 1
        if keys[pygame.K_LEFT]:
            self.velocity.x -= 1
        if keys[pygame.K_UP]:
            self.velocity.y -= 1
        if keys[pygame.K_DOWN]:
            self.velocity.y += 1

        if self.velocity.length() > 0:
            self.velocity = self.velocity.normalize() * self.speed

        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # Collision detection with screen boundaries
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.rect.x -= self.velocity.x
        if self.rect.top < 0 or self.rect.bottom > screen_height:
            self.rect.y -= self.velocity.y

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)

class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)

class Goal:
    def __init__(self, x, y, radius):
        self.circle = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)
        self.radius = radius

    def draw(self, surface):
        pygame.draw.circle(surface, GREEN, self.circle.center, self.radius)

    def check_collision(self, player_rect):
        if self.circle.colliderect(player_rect):
            self.on_collision()

    def on_collision(self):
        print("You won!")

# Initialize player, walls, and goal
player = Player(screen_width // 2, screen_height // 2)
walls = [
    Wall(300, 300, 100, 100),
    Wall(500, 150, 150, 200)
]
goal = Goal(700, 500, 25)

def game_update():
    """ Update game logic for one tick """
    player.update()

    # Collision detection with walls
    for wall in walls:
        if player.rect.colliderect(wall.rect):
            player.rect.x -= player.velocity.x
            player.rect.y -= player.velocity.y
            break

    # Check collision with goal
    goal.check_collision(player.rect)

def draw_scene():
    """ Draw the game scene """
    screen.fill(BLACK)
    player.draw(screen)
    for wall in walls:
        wall.draw(screen)
    goal.draw(screen)
    
    # Draw raycast
    center_of_screen = (screen_width // 2, screen_height // 2)
    start_pos = player.rect.center
    end_pos = center_of_screen
    color = BLUE

    for wall in walls:
        if get_line_intersection(start_pos, end_pos, (wall.rect.topleft, wall.rect.topright)) or \
           get_line_intersection(start_pos, end_pos, (wall.rect.topright, wall.rect.bottomright)) or \
           get_line_intersection(start_pos, end_pos, (wall.rect.bottomright, wall.rect.bottomleft)) or \
           get_line_intersection(start_pos, end_pos, (wall.rect.bottomleft, wall.rect.topleft)):
            color = YELLOW
            break

    pygame.draw.line(screen, color, start_pos, end_pos, 2)
    
    # Draw raycasts
    for start_pos, end_pos in raycast_intersections:
        pygame.draw.line(screen, PURPLE, start_pos, end_pos, 2)
    
    pygame.display.flip()

def cast_ray(start_pos, direction, max_length=1000):
    """ Cast a ray from start_pos in a given direction """
    end_pos = (start_pos[0] + direction[0] * max_length,
               start_pos[1] + direction[1] * max_length)
    closest_intersection = None
    min_distance = max_length

    for wall in walls:
        intersections = get_rect_line_intersections(wall.rect, start_pos, end_pos)
        for intersection in intersections:
            distance = math.hypot(intersection[0] - start_pos[0], intersection[1] - start_pos[1])
            if distance < min_distance:
                min_distance = distance
                closest_intersection = intersection

    if closest_intersection:
        return start_pos, closest_intersection
    return start_pos, end_pos

def get_rect_line_intersections(rect, start_pos, end_pos):
    """ Get the intersections of a line with a rectangle """
    rect_lines = [
        ((rect.left, rect.top), (rect.right, rect.top)),
        ((rect.right, rect.top), (rect.right, rect.bottom)),
        ((rect.right, rect.bottom), (rect.left, rect.bottom)),
        ((rect.left, rect.bottom), (rect.left, rect.top))
    ]

    intersections = []
    for line_start, line_end in rect_lines:
        intersection = get_line_intersection(start_pos, end_pos, (line_start, line_end))
        if intersection:
            intersections.append(intersection)
    
    return intersections

def get_line_intersection(p1, p2, p3p4):
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

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and require_space_to_advance:
                game_update()
            if event.key == pygame.K_r:
                # Shoot a ray from player position to the right
                direction = (1, 0)
                start_pos, end_pos = cast_ray(player.rect.center, direction)
                raycast_intersections.append((start_pos, end_pos))

    if not require_space_to_advance:
        game_update()

    draw_scene()
    clock.tick(60)
