from typing import List
from typing import List
import pygame
from math import radians, degrees, pi

import sys

pygame.init()

SCREEN_WIDTH = 760
SCREEN_HEIGHT = 760


# координаты точки 0, 0
PX_X_ZERO = 672  
PX_Y_ZERO = 672

BLACK = (0, 0, 0)

font = pygame.font.Font(None, 16)
click_pos = None
is_drop = False
is_available = False
is_pickup = False
is_goto = False
is_screenshot = False

PIXELS_PER_METER = 579 / 6.153  # 579 - ширина в px, 6.153 - длина помещения в метрах
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Detected objects")


def load_image(src: str) -> pygame.Surface:
    item_img = pygame.image.load(src).convert()  
    item_img.set_colorkey((255, 255, 255))

    return item_img


def pixels_to_meters(pixels: int, scale: float=PIXELS_PER_METER) -> float:
    return pixels / scale


def meters_to_pixels(meters: float, scale: float=PIXELS_PER_METER) -> int:
    return int(meters * scale)
    

def blit_image(surface: pygame.Surface, item_x_meters: float, item_y_meters: float, yaw_data: int = 0, count: int = None) -> None:
    size_x, size_y = surface.get_size()
    
    pix_pose = [-meters_to_pixels(item_x_meters), -meters_to_pixels(item_y_meters)]
    size_offset = [-size_y * 2 / 3, -size_x // 2]
    
    x = pix_pose[1] + PX_X_ZERO + size_offset[1]
    y = pix_pose[0] + PX_Y_ZERO + size_offset[0]
    
    rotated_img = pygame.transform.rotate(surface, degrees(yaw_data))
    
    screen.blit(rotated_img, (x, y)) 
    
    if count is None:
        text_surface = font.render(f"X: {round(item_x_meters,1)} Y: {round(item_y_meters,1)}", True, BLACK)  # Текст, сглаживание, цвет
    else:
        text_surface = font.render(f"X: {round(item_x_meters,1)} Y: {round(item_y_meters,1)} C: {count}", True, BLACK)  # Текст, сглаживание, цвет

    size_x, size_y = text_surface.get_size()
    size_offset = [size_y + 2, -size_x // 2]
    
    x = pix_pose[1] + PX_X_ZERO + size_offset[1]
    y = pix_pose[0] + PX_Y_ZERO + size_offset[0]
    
    screen.blit(text_surface, (x, y)) 


def get_click_pose() -> List[float]:
    global click_pos
    px_pos = click_pos
    pos = [
        -pixels_to_meters(px_pos[1] - PX_Y_ZERO),
        -pixels_to_meters(px_pos[0] - PX_X_ZERO),
    ]
    return pos


def get_is_drop() -> bool:
    global is_drop
    if is_drop:
        is_drop = False
        return True
    return False


def get_is_pickup() -> bool:
    global is_pickup
    if is_pickup:
        is_pickup = False
        return True
    return False


def get_is_available() -> bool:
    global is_available
    if is_available:
        is_available = False
        return True
    return False


def get_is_goto() -> bool:
    global is_goto
    if is_goto:
        is_goto = False
        return True
    return False

def get_is_screenshot() -> bool:
    global is_screenshot
    if is_screenshot:
        is_screenshot = False
        return True
    return False

def draw_grid(screen: pygame.Surface):
    for ind_x in range(-20, 20):
        pygame.draw.line(screen, (150, 150, 150), (PX_X_ZERO + PIXELS_PER_METER * ind_x, 0), (PX_X_ZERO + PIXELS_PER_METER * ind_x, 1_000))
    
    for ind_y in range(-20, 20):
        pygame.draw.line(screen, (150, 150, 150), (0, PX_Y_ZERO + PIXELS_PER_METER * ind_y), (1_000, PX_Y_ZERO + PIXELS_PER_METER * ind_y))

    pygame.draw.rect(screen, (255, 100, 100), ((PX_X_ZERO - meters_to_pixels(6.15), PX_Y_ZERO - meters_to_pixels(6.15)), (meters_to_pixels(6.15), meters_to_pixels(6.15))), 1)


health_img = load_image('imgs/health.png')
fire_img = load_image('imgs/fire.png')
route_img = load_image('imgs/route.png')
drone_img = load_image('imgs/drone.png')

rover_img = load_image('imgs/rover.png')


def update(drone_coordinate: List, route: List,
           health_coordinates: List=[],
           fire_coordinates: List=[], is_drone: bool=True) -> None:
    
    global click_pos, is_drop, is_available, is_pickup, is_goto, is_screenshot
    global screen, fire_img, health_img, drone_img, route_img
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pass
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                is_drop = True
            elif event.button == 2:
                is_available = True
            elif event.button == 3:
                is_pickup = True
            click_pos = event.pos
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                is_goto = True
            if event.key == pygame.K_SPACE:
                is_screenshot = True
                
                
    
    screen.fill((255,255,255))
    draw_grid(screen)
    
    for point in route:
        blit_image(route_img, *point[:2], point[2])
    
    for fire_coordinate in fire_coordinates:
        blit_image(fire_img, *fire_coordinate["point"], count=fire_coordinate["count"])
    
    for health_coordinate in health_coordinates:
        blit_image(health_img, *health_coordinate["point"], count=health_coordinate["count"])
    
    
    if is_drone:
        blit_image(drone_img, *drone_coordinate)
    else:
        blit_image(rover_img, *drone_coordinate)

    pygame.display.flip()


if __name__ == "__main__":
    running = True
    while running:
        update([0.32, 2.27, 1.39], [], [], [{"point": [-0.060139301139942536, 4.687027581278922], "count": 100}])
    #     update([0,0, pi/2],
    # [
    # [4.25,0, radians(0)],
    # [0.5, 0, radians(180)],
    # [0.5, 3, radians(90)],
    # [1.5, 3, radians(0)],
    # [1.5, 5.5, radians(90)],
    # [0.0, 5.5, radians(180)],
    # [1.5, 5.5, radians(0)],
    # [1.5, 3, radians(-90)],
    # [0.5, 3, radians(180)],
    # [0.5, 0, radians(-90)],
    # [0.0, 0, radians(180)],
    # ])

    pygame.quit()
    sys.exit()
