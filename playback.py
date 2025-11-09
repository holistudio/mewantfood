import pygame
import sys
import math
import json

PACMAN_MODE = True

info_json = 'info.json'
playback_json = 'record.json'

with open(info_json, 'r') as f:
    info = json.load(f)
with open(playback_json, 'r') as f:
    trajectory = json.load(f)['trajectory']


def polar_to_cartesian(r, theta):
    # assume theta is in degrees
    theta_rad = theta * math.pi / 180
    x = r * math.cos(theta_rad)
    y = r * math.sin(theta_rad)
    return x, y

def cartesian_to_polar(x, y):
    # Convert to polar
    r = math.sqrt(x**2 + y**2)
    theta = math.degrees(math.atan2(y, x))
    return r, theta

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600

TABLE_RADIUS = info['radius']

if PACMAN_MODE:
    AGENT_SIZE = 15
    FOOD_SIZE = AGENT_SIZE // 2
else:
    AGENT_SIZE = FOOD_SIZE = 15

agent_locations = [(p[0],p[1]) for p in info['player_locations']]
# mouth_locations = [(a[0]-12,a[1]) for a in agent_locations]


agent_forwards = []
for x, y in agent_locations:
    r, theta = cartesian_to_polar(x, y)
    theta_rad = theta * math.pi / 180
    # unit vector pointing towards the center (0,0) from the agent's location
    unit_vector = (-math.cos(theta_rad), -math.sin(theta_rad))
    agent_forwards.append(unit_vector)





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
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

if PACMAN_MODE:
    BG_COLOR = BLACK
    STROKE_COLOR = BLUE
    AGENT_COLOR = YELLOW
    FOOD_COLOR = WHITE
else:
    BG_COLOR = WHITE
    STROKE_COLOR = BLACK
    AGENT_COLOR = BLACK
    FOOD_COLOR = RED

THIN_STROKE = 1
THICK_STROKE = 2

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

    screen.fill(BG_COLOR)

    # Draw the table
    pygame.draw.circle(screen, STROKE_COLOR, (screen_width // 2, screen_height // 2), TABLE_RADIUS, THIN_STROKE)

    # Draw spoons
    for i, (x, y) in enumerate(agent_locations):
        # Agent's center in screen coordinates
        agent_x_cart, agent_y_cart = x,y
        start_x = int(screen_width / 2 + agent_x_cart)
        start_y = int(screen_height / 2 + agent_y_cart)

        # Calculate the spoon's absolute angle
        # The agent's forward direction angle is theta + 180.
        r, theta = cartesian_to_polar(x, y)
        spoon_angle = theta + 180 + spoon_thetas[i]
        end_x_cart, end_y_cart = polar_to_cartesian(spoon_lengths[i], spoon_angle)
        end_x = start_x + int(end_x_cart)
        end_y = start_y + int(end_y_cart)
        pygame.draw.line(screen, STROKE_COLOR, (start_x, start_y), (end_x, end_y), THICK_STROKE)
        
        # Draw spoon head (ellipse)
        # Draw filled white ellipse
        draw_rotated_ellipse(screen, BG_COLOR, (end_x, end_y), 10, 5, spoon_angle)
        # Draw black outline
        draw_rotated_ellipse(screen, STROKE_COLOR, (end_x, end_y), 10, 5, spoon_angle, THICK_STROKE)
    
    # Draw food
    for x, y in food_locations:
        screen_x = int(screen_width / 2 + x)
        screen_y = int(screen_height / 2 + y)
        if PACMAN_MODE:
            pygame.draw.circle(screen, FOOD_COLOR, (screen_x, screen_y), FOOD_SIZE)
        else:
            pygame.draw.rect(screen, FOOD_COLOR, (screen_x - FOOD_SIZE // 2, screen_y - FOOD_SIZE // 2, FOOD_SIZE, FOOD_SIZE))

    

    # Draw agents
    for x, y in agent_locations:
        screen_x = int(screen_width / 2 + x)
        screen_y = int(screen_height / 2 + y)
        pygame.draw.circle(screen, AGENT_COLOR, (screen_x, screen_y), AGENT_SIZE)
    for i, (x, y) in enumerate(agent_locations):
        if agent_mouths[i]:
            screen_x = int(screen_width / 2 + x)
            screen_y = int(screen_height / 2 + y)

            x1, y1 = agent_locations[i]
            x1 = int(screen_width / 2 + x1)
            y1 = int(screen_height / 2 + y1)
            
            forward_x, forward_y = agent_forwards[i]
            
            # p2 and p3 are perpendicular to the forward vector
            p2_x = x1 + forward_x * AGENT_SIZE - (-forward_y) * AGENT_SIZE
            p2_y = y1 + forward_y * AGENT_SIZE - forward_x * AGENT_SIZE
            p3_x = x1 + forward_x * AGENT_SIZE + (-forward_y) * AGENT_SIZE
            p3_y = y1 + forward_y * AGENT_SIZE + forward_x * AGENT_SIZE
            
            x2, y2 = p2_x, p2_y
            x3, y3 = p3_x, p3_y
            pygame.draw.polygon(screen, BG_COLOR, [(x1, y1), (x2, y2), (x3, y3)])
            # else:
            #     pygame.draw.circle(screen, BG_COLOR, (screen_x, screen_y), 4)

    

    

    pygame.display.flip()
    clock.tick(fps)
    frame_counter += 1

pygame.quit()
sys.exit()