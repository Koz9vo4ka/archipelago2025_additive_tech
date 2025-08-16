from typing import List, Dict
import grock_algoritm 
import view_math
import json


class ObjectManager:
    def __init__(self) -> None:
        """
        Инициализация определения цветов в пространстве.
        """
        # Угол обзора
        self.__FOV = 95
        # Трешхолд по площади детекции (не активен)
        self.__MIN_AREA_FLOWER = 0
        # Соотношение сторон изображения
        self.__ASPECT_RATIO = 4 / 3

        # Обнаруженные цветы
        self.__finded_flowers = []
        # Последняя детекция
        self.__last_detections = None
    
    def get_sorted_detections(self) -> List[List[Dict]]:
        # Объединяем объекты, если они находятся неподалёку
        sorted_by_dict = {}
        
        finded_flowers = self.__create_grouped_data(self.__finded_flowers)
        
        for name, data in finded_flowers.items():
            mean_flowers = grock_algoritm.calc_mean_objects(data)
            
            # Сортируем объекты по количеству обнаружений
            sorted_mean_flowers = sorted(mean_flowers, key=lambda mean_flower: mean_flower["count"], reverse=True)
            sorted_by_dict[name] = sorted_mean_flowers

        return sorted_by_dict
    
    def __create_grouped_data(self, objects: List[Dict]) -> Dict[Dict, List]:
        grouped_data = {}
        
        for item in objects:
            name = item['name']
            coords = item['coordinates']
            
            if name not in grouped_data:
                grouped_data[name] = []
            
            grouped_data[name].append(coords)
        
        return grouped_data

    def process_detections(self, detections: Dict, current_pos: List[float], rpy: List[float]) -> None:
        """
        Обрабатывает данные полученные от нейронной сети
        
        detections - data from yolo
        current_pos - x, y, z in meters
        rpy - roll, pitch, yaw in radians
        """
        # Если данные не обновились, то ничего не делаем
        if not self.__check_detections(detections):
            return
        
        # Обрабатываем и фильтруем данные
        detections_with_pos = self.__calc_real_pos_of_detection(detections, current_pos, rpy)
        filtred_detections_with_pos = self.__filter_by_area(detections_with_pos)

        # Добавляем обнаруженные объекты
        self.__add_finded_objects(filtred_detections_with_pos)

    # region data processing
    # =================== data from drone filtering and transform =============

    def __check_detections(self, current_detections):
        """
        Проверка что данные не пустые и не повторяются
        """
        
        if current_detections == {}:
            return
        
        if current_detections != self.__last_detections:
            self.__last_detections = current_detections
            return True
        return False

    def __calc_real_pos_of_detection(self, detections: Dict, current_pos: List[float], rpy: List[float]) -> List[Dict]:
        """
        Рассчитывает положение обнаруженных объектов
        
        detections - data from yolo
        current_pos - x, y, z in meters
        rpy - roll, pitch, yaw in radians
        """
        
        objs = []
        WIDTH = detections["image_width"]
        HEIGHT = detections["image_height"]

        for detection in detections["boxes"]:
            # Определение типа объекта
            abs_pos = self.__calc_abs_pos(detection["center"]["x"] / WIDTH, detection["center"]["y"] / HEIGHT, current_pos, rpy)

            # Добавляем новый объект
            objs.append({
                "name": detection["name"],
                "area": detection["area"],
                "position": abs_pos,
            })
        
        return objs

    def __calc_abs_pos(self, center_x: float, center_y: float, current_pos: List[float], rpy: List[float]) -> List[float]:
        """
        Рассчитывает положение обнаруженного объекта
        
        center_x, center_y - нормированое положение цетра рамки на экране
        current_pos - x, y, z in meters
        rpy - roll, pitch, yaw in radians
        """
        
        # Углы на объект в глобальной системе координат
        a, b = view_math.calc_abs_ang(center_x, center_y, rpy[0], rpy[1], self.__FOV, self.__ASPECT_RATIO)
        
        # Позиция в системе координат дрона
        local_pos = view_math.calc_local_pos(a, b, current_pos[2])
        
        # Относительное положение
        relative_pos = view_math.calc_relative_pos(*local_pos, rpy[2])

        # Абсолютное положение
        abs_pos = view_math.calc_abs_pos(*relative_pos, *current_pos[:2])

        return abs_pos

    def __filter_by_area(self, objects: List[Dict]) -> List[Dict]:
        """
        Фильтрация обнаруженных объектов по площади bbox'a
        
        objects - данные в формате [{"name": "red_flower", "area": 100, "position": [3.435, 1.543]}, {...}, ...]
        """
        
        filtred_detections = []

        for detection in objects:
            if detection["area"] > self.__MIN_AREA_FLOWER:
                filtred_detections.append(detection)
        
        return filtred_detections

    def __add_finded_objects(self, objs: List) -> None:
        """
        Добавление обнаруженных объектов
        
        objects - данные в формате [{"name": "red_flower", "area": 100, "position": [3.435, 1.543]}, {...}, ...]
        """
        
        for obj in objs:
            name = obj["name"]
            pose = obj["position"]

            data = {
                "name": name,
                "coordinates": pose,
            }

            self.__finded_flowers.append(data) 


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

    if is_test:
        for i in range(10):
            d1 = create_detection("red_flower", 320, 240, 100, 270)
            # d2 = create_detection("green_flower", 100, 100, 100, 270)
            # d3 = create_detection("white_flower", 1400, 10, 100, 270)

            # d4 = create_detection("red_flower", 10, 1000, 100, 270)
            ds = create_detections([d1])

            obj_manager.process_detections(ds, [0, 0, 1.0], [0, 0, 0])
            # obj_manager.get_sorte d_detections()


        sorted_mean_flowers = obj_manager.get_sorted_detections()
        print(sorted_mean_flowers)

        while False:
            pygame_map.update([0, 0], mean_finded_flower, mean_finded_fire)
            pygame_map.route(TARGETS)