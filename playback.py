import pygame
import sys
import math
import json

info_json = 'info.json'
playback_json = 'record.json'

with open(info_json, 'r') as f:
    info = json.load(f)
with open(playback_json, 'r') as f:
    trajectory = json.load(f)['trajectory']

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600

TABLE_RADIUS = info['radius']

AGENT_SIZE = FOOD_SIZE = 10

agent_locations = [(p[0],p[1]) for p in info['player_locations']]
mouth_locations = [(a[0]-5,a[1]) for a in agent_locations]


agent_forwards = []
for r, theta in agent_locations:
    theta_rad = theta * math.pi / 180
    # unit vector pointing towards the center (0,0) from the agent's location
    unit_vector = (-math.cos(theta_rad), -math.sin(theta_rad))
    agent_forwards.append(unit_vector)



def polar_to_cartesian(r, theta):
    # assume theta is in degrees
    theta_rad = theta * math.pi / 180
    x = r * math.cos(theta_rad)
    y = r * math.sin(theta_rad)
    return x, y

def draw_rotated_ellipse(surface, color, rect_center, r1, r2, angle, width=0):
    """Draws a rotated ellipse on a surface."""
    target_rect = pygame.Rect(rect_center, (0, 0)).inflate((r1 * 2, r2 * 2))
    ellipse_surface = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(ellipse_surface, color, (0, 0, r1 * 2, r2 * 2), width)
    
    rotated_surface = pygame.transform.rotate(ellipse_surface, -angle)
    
    surface.blit(rotated_surface, rotated_surface.get_rect(center=rect_center))

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
total_frames = len(trajectory) * fps

frame_counter = 0
running = True
while running and frame_counter < total_frames:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    idx = frame_counter // fps
    spoon_lengths = trajectory[idx]['spoon_lengths']
    spoon_thetas = trajectory[idx]['spoon_thetas']
    food_locations  = trajectory[idx]['food_locations']
    agent_mouths = trajectory[idx]['player_mouths_open']

    screen.fill(WHITE)

    # Draw the table
    pygame.draw.circle(screen, BLACK, (screen_width // 2, screen_height // 2), TABLE_RADIUS, 1)

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
        spoon_angle = theta + 180 + spoon_thetas[i]
        end_x_cart, end_y_cart = polar_to_cartesian(spoon_lengths[i], spoon_angle)
        end_x = start_x + int(end_x_cart)
        end_y = start_y + int(end_y_cart)
        pygame.draw.line(screen, BLACK, (start_x, start_y), (end_x, end_y), 2)
        
        # Draw spoon head (ellipse)
        # Draw filled white ellipse
        draw_rotated_ellipse(screen, WHITE, (end_x, end_y), 10, 5, spoon_angle)
        # Draw black outline
        draw_rotated_ellipse(screen, BLACK, (end_x, end_y), 10, 5, spoon_angle, 2)

    # Draw agents
    for r, theta in agent_locations:
        x, y = polar_to_cartesian(r, theta)
        screen_x = int(screen_width / 2 + x)
        screen_y = int(screen_height / 2 + y)
        pygame.draw.circle(screen, BLACK, (screen_x, screen_y), AGENT_SIZE)
    for i, (r, theta) in enumerate(mouth_locations):
        if agent_mouths[i]:
            x, y = polar_to_cartesian(r, theta)
            screen_x = int(screen_width / 2 + x)
            screen_y = int(screen_height / 2 + y)
            pygame.draw.circle(screen, WHITE, (screen_x, screen_y), 4)

    

    

    pygame.display.flip()
    clock.tick(fps)
    frame_counter += 1

pygame.quit()
sys.exit()