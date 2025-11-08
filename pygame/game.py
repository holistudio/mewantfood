import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600

agent_locations = [(200,0), (200,90), (200,180), (200,270)]
mouth_locations = [(a[0]-5,a[1]) for a in agent_locations]
food_locations  = [(160,0), (160,90), (160,180), (160,270)]

def polar_to_cartesian(r, theta):
    # assume theta is in degrees
    theta_rad = theta * math.pi / 180
    x = r * math.cos(theta_rad)
    y = r * math.sin(theta_rad)
    return x, y

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("mewantfood")

# Clock for controlling the frame rate
clock = pygame.time.Clock()
fps = 30

# Total frames for 10 seconds
total_frames = 10 * fps

frame_counter = 0
running = True
while running and frame_counter < total_frames:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    # Draw the table
    pygame.draw.circle(screen, BLACK, (screen_width // 2, screen_height // 2), 180, 1)

    # Draw agents
    for r, theta in agent_locations:
        x, y = polar_to_cartesian(r, theta)
        screen_x = int(screen_width / 2 + x)
        screen_y = int(screen_height / 2 + y)
        pygame.draw.circle(screen, BLACK, (screen_x, screen_y), 10)
    for r, theta in mouth_locations:
        x, y = polar_to_cartesian(r, theta)
        screen_x = int(screen_width / 2 + x)
        screen_y = int(screen_height / 2 + y)
        pygame.draw.circle(screen, WHITE, (screen_x, screen_y), 4, 1)

    # Draw food
    food_size = 5
    for r, theta in food_locations:
        x, y = polar_to_cartesian(r, theta)
        screen_x = int(screen_width / 2 + x)
        screen_y = int(screen_height / 2 + y)
        pygame.draw.rect(screen, RED, (screen_x - food_size // 2, screen_y - food_size // 2, food_size, food_size))

    pygame.display.flip()
    clock.tick(fps)
    frame_counter += 1

pygame.quit()
sys.exit()