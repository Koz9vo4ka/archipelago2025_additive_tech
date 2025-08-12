from typing import List
import pygame

import sys


class DroneDataVisualization:
    def __init__(self) -> None:
        
        pygame.init()
        pygame.font.init()

        
        self.__WHITE = (255, 255, 255)
        
        self.__is_screenshot = False
        
        self.__size = [self.__width, self.__height] = [760, 760]
        self.__screen = pygame.display.set_mode(self.__size)
        self.__font = pygame.font.SysFont(None, 20)
        pygame.display.set_caption("drone data vizualization")
                
        self.__zero = [672, 672]  # координаты точки 0, 0 в пикселях
        self.__offset = [0, 0]  # в метрах
        
        self.__ROUTE_IMG = self.__load_image('imgs/route.png')
        self.__DRONE_IMG = self.__load_image('imgs/drone.png')
        
        # TODO сделать словарём
        self.__LIST_FLOWERS = [self.__load_image('imgs/white_flower.png'), self.__load_image('imgs/red_flower.png'), self.__load_image('imgs/purple_flower.png')]
        
        self.__DRONE_IMG = self.__load_image('imgs/drone.png')
        
        self.pole_size = [8, 8]

        self.__PIXELS_PER_METER = 565 / max(self.pole_size)  # 579 - ширина в px, 6.153 - длина помещения в метра

    def __load_image(self, src: str, color_key: List=[255, 255, 255]) -> pygame.Surface:
        item_img = pygame.image.load(src).convert()  
        item_img.set_colorkey(color_key)

        return item_img

    @property
    def zero_px(self) -> List[float]:
        return [self.__zero[0] + self.__offset[0] * self.__PIXELS_PER_METER, self.__zero[1] + self.__offset[1] * self.__PIXELS_PER_METER]

    def __meters_2_pixels(self, x: float, y: float = 0) -> List[float]:
        return [
            -x * self.__PIXELS_PER_METER + self.zero_px[1],  # на экране ось направленна вниз, нам надо вверх
            -y * self.__PIXELS_PER_METER + self.zero_px[0]  # на экране ось направлена вправо, нам надо влево
        ]
    
    def __m_2_px(self, pixels) -> List[float]:
        return int(pixels * self.__PIXELS_PER_METER)
    
    def __blit_coordinates(self, x_meters: float, y_meters: float, picture_offset: int = 30) -> None:
        text_surface = self.__font.render(f"X: {round(x_meters,1)} Y: {round(y_meters,1)}", True, self.__WHITE)  # Текст, сглаживание, цвет
        size_x, _ = text_surface.get_size()
        surface_size_offset = [picture_offset, -size_x // 2]
        
        x, y = self.__meters_2_pixels(y_meters, x_meters)

        self.__screen.blit(text_surface, (x + surface_size_offset[1], y + surface_size_offset[0])) 

    def __blit_image(self, surface: pygame.Surface, x_meters: float, y_meters: float, yaw_data: int = 0) -> None:
        x, y = self.__meters_2_pixels(y_meters, x_meters)

        rotated_img = pygame.transform.rotate(surface, yaw_data)
        
        size_x, size_y = rotated_img.get_size()
        surface_size_offset = [-size_y // 2, -size_x // 2]
        
        self.__screen.blit(rotated_img, (x + surface_size_offset[1], y + surface_size_offset[0])) 

    def get_is_screenshot(self) -> bool:
        if self.__is_screenshot:
            self.__is_screenshot = False
            return True
        return False

    def __draw_grid(self) -> None:
        for ind_x in range(-20, 20):
            pygame.draw.line(self.__screen, (150, 150, 150), (self.zero_px[0] + self.__PIXELS_PER_METER * ind_x, 0), (self.zero_px[0] + self.__PIXELS_PER_METER * ind_x, 1_000))
        
        for ind_y in range(-20, 20):
            pygame.draw.line(self.__screen, (150, 150, 150), (0, self.zero_px[1] + self.__PIXELS_PER_METER * ind_y), (1_000, self.zero_px[1] + self.__PIXELS_PER_METER * ind_y))
            
        x, y = self.__meters_2_pixels(self.pole_size[0]+1, self.pole_size[1]+1)
        
        x_1,y_1 = self.__meters_2_pixels(-0.5, -0.5)

        pygame.draw.rect(self.__screen,
            (255, 100, 100),
            (x, y, x_1, y_1),
            1
        )

    def update(self, drone_coordinate: List, route: List, flowers: List=[int, List]) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.__is_screenshot = True

        self.__screen.fill((36,105,61))
        self.__draw_grid()
        
        for id_flower, flower_coordinate in flowers:
            self.__blit_image(self.__LIST_FLOWERS[id_flower], *flower_coordinate)
            self.__blit_coordinates(*flower_coordinate)
        
        # TODO у нас нет пути
        for point in route:
            self.__blit_image(self.__ROUTE_IMG, *point[:2], point[2])
            self.__blit_coordinates(*point[:2])

        self.__blit_image(self.__DRONE_IMG, *drone_coordinate)
        
        self.__blit_coordinates(*drone_coordinate[:2])

        pygame.display.flip()

    def run(self, ) -> None:
        while True:
            self.update([0, 0.0, 0], [], [[1, [1, 5]], [0, [1, 6]], [2, [1, 7]]])


if __name__ == "__main__":
    Pygame_screen = DroneDataVisualization()
    Pygame_screen.run()

    # pygame.quit()
    # sys.exit()
