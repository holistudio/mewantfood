import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600

AGENT_SIZE = FOOD_SIZE = 10

agent_locations = [(200,0), (200,90), (200,180), (200,270)]
mouth_locations = [(a[0]-5,a[1]) for a in agent_locations]
food_locations  = [(160,0), (160,90), (160,180), (160,270)]

agent_forwards = []
for r, theta in agent_locations:
    theta_rad = theta * math.pi / 180
    # unit vector pointing towards the center (0,0) from the agent's location
    unit_vector = (-math.cos(theta_rad), -math.sin(theta_rad))
    agent_forwards.append(unit_vector)

spoon_angles = [0, 10, -10, -45]

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
        pygame.draw.circle(screen, BLACK, (screen_x, screen_y), AGENT_SIZE)
    for r, theta in mouth_locations:
        x, y = polar_to_cartesian(r, theta)
        screen_x = int(screen_width / 2 + x)
        screen_y = int(screen_height / 2 + y)
        pygame.draw.circle(screen, WHITE, (screen_x, screen_y), 4)

    # Draw food
    for r, theta in food_locations:
        x, y = polar_to_cartesian(r, theta)
        screen_x = int(screen_width / 2 + x)
        screen_y = int(screen_height / 2 + y)
        pygame.draw.rect(screen, RED, (screen_x - FOOD_SIZE // 2, screen_y - FOOD_SIZE // 2, FOOD_SIZE, FOOD_SIZE))

    # Draw spoons
    for i, (r, theta) in enumerate(agent_locations):
        # Agent's center in screen coordinates
        agent_x_cart, agent_y_cart = polar_to_cartesian(r, theta)
        start_x = int(screen_width / 2 + agent_x_cart)
        start_y = int(screen_height / 2 + agent_y_cart)

        # Calculate the spoon's absolute angle
        spoon_angle = theta + 180 + spoon_angles[i]
        end_x_cart, end_y_cart = polar_to_cartesian(180, spoon_angle)
        end_x = start_x + int(end_x_cart)
        end_y = start_y + int(end_y_cart)
        pygame.draw.line(screen, BLACK, (start_x, start_y), (end_x, end_y), 2)

    pygame.display.flip()
    clock.tick(fps)
    frame_counter += 1

pygame.quit()
sys.exit()