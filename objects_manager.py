"""
Предоставляет функции:
process_detections(detections) - для обработки полученных данных
get_detections() - для получения итоговых координат людей и огней
save_detections() - для сохранения итоговых данных

get_json_data() - для получения данных из файла
"""


from enum import IntEnum
from typing import List, Dict
import grock_algoritm 
import view_math
import json
from math import radians, cos, sin
from test_dist_eval import calc_dist

class Objects(IntEnum):
    RED_FLOWER = 1
    WHITE_FLOWER = 2
    GREEN_FLOWER = 3


# region core functions
# =================== core functions =============


class ObjectManager:
    def __init__(self) -> None:
        self.__finded_flower = []
        self.__FOV = 95
        self.__last_detections = None
        self.__MIN_AREA_FLOWER = 0
        self.__WIDTH = 0
        self.__ASPECT_RATIO = 4 / 3
        self.__alt = 0.5
    
    def get_sorted_detections(self) -> List[List[Dict]]:
        mean_flowers = grock_algoritm.calc_mean_objects(list(map(lambda flower: flower["coordinates"], self.__finded_flower)))

        sorted_mean_flowers = sorted(mean_flowers, key=lambda mean_flower: mean_flower["count"], reverse=True)

        return sorted_mean_flowers

    def process_detections(self, detections: Dict, current_pos: List[float], yaw: float) -> None:
        # Если данные не обновились, то ничего не делаем
        if not self.check_detections(detections):
            return
        
        # Фильтруем данные
        detections_with_pos = self.calc_real_pos_of_detection(detections, current_pos, yaw)
        filtred_detections_with_pos = self.filter_by_area(detections_with_pos)

        self.add_finded_objects(filtred_detections_with_pos)

    def get_json_data(json_file):
        try:
            with open(json_file, 'r') as f:
                content = f.read()
                data = json.loads(content)
                return data

        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")


    # region data processing
    # =================== data from drone filtering and transform =============

    def check_detections(self, current_detections):
        if current_detections == {}:
            return
        
        if current_detections != self.__last_detections:
            self.__last_detections = current_detections
            return True
        return False

    def calc_real_pos_of_detection(self, detections: Dict, current_pos: List[float], yaw: float) -> List[Dict]:
        """
        current_x, current_y in meters
        yaw in radians
        """

        objs = []
        WIDTH = detections["image_width"]

        for detection in detections["boxes"]:
            # Определение типа объекта
            abs_pos = self.calc_abs_pos(current_pos, yaw, detection["center"]["x"], detection["center"]["y"], WIDTH)

            # Добавляем новый объект
            objs.append({
                "name": detection["name"],
                "area": detection["area"],
                "position": abs_pos,
            })
        
        return objs

    def calc_abs_pos(self, current_pose: List[float], current_yaw: float, center_x: float, center_y: float, alt: float=0.5) -> List[float]:
        # Рассчёт глобального курса
        a, b = view_math.calc_abs_ang(center_x, center_y, 0, 0, self.__FOV, self.__ASPECT_RATIO)
        local_pose = view_math.calc_local_pos(a, b, alt)
        
        # Относительное положение
        relative_pos = view_math.calc_relative_pos(*local_pose, current_yaw)

        # Абсолютное положение
        abs_pos = view_math.calc_abs_pos(*relative_pos, *current_pose)

        return abs_pos

    def filter_by_area(self, detections: List[Dict]) -> List[Dict]:
        filtred_detections = []

        for detection in detections:
            if detection["area"] > self.__MIN_AREA_FLOWER:
                filtred_detections.append(detection)

        
        return filtred_detections

    def add_finded_objects(self, objs: List) -> None:
        for obj in objs:
            name = obj["name"]
            pose = obj["position"]

            data = {
                "name": name,
                "coordinates": pose,
            }
            
            self.__finded_flower.append(data)   


# region tests
if __name__ == "__main__":
    is_test = True
    obj_manager = ObjectManager()
    if is_test:
        def create_detections(detections: List):
            return {
                "boxes": detections,
                "image_height": 480,
                "image_width": 640
            }


        def create_detection(name: str, center_x: float, area: float, size_x: float, size_y: float) -> Dict:
            return {
                "name": name, 
                "center": { "x": center_x, "y": 0, "theta": 0},
                "area": area, 
                "size_x": size_x, 
                "size_y": size_y 
            }

        alt = 0.5

    if is_test:
        for i in range(10):
            d1 = create_detection("red_flower", 1030, 1000, 100, 170)
            d2 = create_detection("green_flower", 100, 100, 100, 170)
            d3 = create_detection("white_flower", 1400, 1000, 100, 170)

            ds = create_detections([d1, d2, d3])

            obj_manager.process_detections(ds, [0, 0], 0)

        sorted_mean_flowers = obj_manager.get_sorted_detections()
        print(sorted_mean_flowers)



        while False:
            pygame_map.update([0, 0], mean_finded_flower, mean_finded_fire)
            pygame_map.route(TARGETS)