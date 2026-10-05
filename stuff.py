# Libraries
import pygame
import sys
import math

# Pygame
WIDTH, HEIGHT = 700, 900
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Colors
GRAY = (128, 128, 128)
PLAYER_YELLOW = (255, 255, 0)
BLACK = (255, 255, 255)

# Variables
player_x = 325.0
player_y = 650.0
player_speed = 5.0
player_radius = 12
player_direction = None
phantom_x = None
phantom_y = None
walls = [
    pygame.Rect(200, 300, 100, 50),
    pygame.Rect(400, 500, 150, 40)
]
keys_pressed = set()
circle_block_x = 350
circle_block_y = 200
circle_block_radius = 40

# Circlue Collision
def check_circle_rect_collision(circle_x, circle_y, radius, rect):
    closest_x = max(rect.left, min(circle_x, rect.right))
    closest_y = max(rect.top, min(circle_y, rect.bottom))
    
    distance_x = circle_x - closest_x
    distance_y = circle_y - closest_y
    
    return (distance_x ** 2 + distance_y ** 2) < (radius ** 2)
# Main Loop
running = True
while running:
    # Exit Game
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
    # Key Detection
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                keys_pressed.add(event.key)
        elif event.type == pygame.KEYUP:
            if event.key in keys_pressed:
                keys_pressed.remove(event.key)

    # Movement And Drawing
    move_x = 0
    move_y = 0
    if pygame.K_d in keys_pressed: move_x += 1
    if pygame.K_a in keys_pressed: move_x -= 1
    if pygame.K_s in keys_pressed: move_y += 1
    if pygame.K_w in keys_pressed: move_y -= 1

    if move_x != 0 or move_y != 0:
        length = math.hypot(move_x, move_y)
        player_x += (move_x / length) * player_speed
        player_y += (move_y / length) * player_speed

    if player_x > WIDTH:  player_x = 0
    if player_x < 0:      player_x = WIDTH
    if player_y > HEIGHT: player_y = 0
    if player_y < 0:      player_y = HEIGHT
    
    for wall in walls:
        closest_x = max(wall.left, min(player_x, wall.right))
        closest_y = max(wall.top, min(player_y, wall.bottom))
        distance_x = player_x - closest_x
        distance_y = player_y - closest_y
        distance = math.hypot(distance_x, distance_y)
        if distance < player_radius:
            if distance != 0:
                overlap = player_radius - distance
                player_x += (distance_x / distance) * overlap
                player_y += (distance_y / distance) * overlap

    distance_x = player_x - circle_block_x
    distance_y = player_y - circle_block_y
    distance = math.hypot(distance_x, distance_y)
    min_distance = player_radius + circle_block_radius
    if distance < min_distance:
        if distance != 0:
            overlap = min_distance - distance
            player_x += (distance_x / distance) * overlap
            player_y += (distance_y / distance) * overlap

    screen.fill(GRAY)
    for wall in walls:
        pygame.draw.rect(screen, BLACK, wall)
    pygame.draw.circle(screen, BLACK, (circle_block_x, circle_block_y), circle_block_radius)
    pygame.draw.circle(screen, PLAYER_YELLOW, (int(player_x), int(player_y)), player_radius)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
sys.exit(0)
