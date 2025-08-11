"""
Предоставляет функции:
process_detections(detections) - для обработки полученных данных
get_detections() - для получения итоговых координат людей и огней
save_detections() - для сохранения итоговых данных

get_json_data() - для получения данных из файла
"""


from enum import IntEnum
from typing import List, Dict
from grock_algoritm import calc_mean_objects, sorted_by_dist
import pygame_map
import json
from math import radians, cos, sin
from test_dist_eval import calc_dist

finded_people = []
finded_fire = []
FOV = 95
last_detections = None


class Objects(IntEnum):
    PEOPLE = 1
    FIRE = 2


# region core functions
# =================== core functions =============


def get_sorted_detections() -> List[List[Dict]]:
    mean_peoples = calc_mean_objects(list(map(lambda peolpe: peolpe["coordinates"], finded_people)))
    mean_fires = calc_mean_objects(list(map(lambda fire: fire["coordinates"], finded_fire)))

    sorted_mean_peoples = sorted(mean_peoples, key=lambda mean_people: mean_people["count"], reverse=True)
    sorted_mean_fires = sorted(mean_fires, key=lambda mean_fire: mean_fire["count"], reverse=True)

    return sorted_mean_peoples, sorted_mean_fires


def save_detections(mean_peoples, mean_fires) -> None: 
    print('save')
    # Сохранение координат людей
    peoples_poses = []
    for mean_people in mean_peoples:
        peoples_poses.append(mean_people["point"])
    
    with open(f'peoples.json', 'w', encoding='utf-8') as file:
            json.dump(peoples_poses, file, ensure_ascii=False, indent=4)

    # Сохранение координат огней
    fires_poses = []
    for mean_fire in mean_fires:
        fires_poses.append(mean_fire["point"])
    
    with open(f'fires.json', 'w', encoding='utf-8') as file:
            json.dump(fires_poses, file, ensure_ascii=False, indent=4)


def process_detections(detections: Dict, current_pos: List[float], yaw: float) -> None:
    # Если данные не обновились, то ничего не делаем
    if not check_detections(detections):
        return
    
    # Фильтруем данные
    detections_with_pos = calc_real_pos_of_detection(detections, current_pos, yaw)
    filtred_detections_with_pos = filter_by_area(detections_with_pos)

    add_finded_objects(filtred_detections_with_pos)


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


def check_detections(current_detections):
    if current_detections == {}:
        return
    
    global last_detections
    
    if current_detections != last_detections:
        last_detections = current_detections
        return True
    return False


def calc_real_pos_of_detection(detections: Dict, current_pos: List[float], yaw: float) -> List[Dict]:
    """
    current_x, current_y in meters
    yaw in radians
    """

    objs = []
    WIDTH = detections["image_width"]

    for detection in detections["boxes"]:
        # Определение типа объекта
        if "human" in detection["name"]:
            object_type = Objects.PEOPLE
            offset_y = 0
        else:
            object_type = Objects.FIRE
            offset_y = detection["size_y"] / 3

        abs_pos = calc_abs_pos(current_pos, yaw, detection["center"]["x"], detection["center"]["y"], offset_y, WIDTH)

        # Добавляем новый объект
        objs.append({
            "name": object_type,
            "area": detection["area"],
            "position": abs_pos,
        })
    
    return objs


def calc_abs_pos(current_pos: float, current_yaw: float, center_x: float, center_y: float, offset_y: float, WIDTH: int=640) -> List[float]:
    # Рассчёт глобального курса
    local_course_rad = -radians((center_x - WIDTH // 2) / WIDTH * FOV)
    global_course_rad = local_course_rad + current_yaw

    # Рассчёт дистанции
    value = center_y + offset_y
    a, b = 3913.85, -6.93
    # multiply is *tempereary solution*
    abs_dist = calc_dist(value, a, b) * 0.9
    
    # Относительное положение
    relative_pos = [
        abs_dist * cos(global_course_rad),
        abs_dist * sin(global_course_rad),
    ]

    # Абсолютное положение
    abs_pos = [
        relative_pos[0] + current_pos[0],
        relative_pos[1] + current_pos[1],
    ]

    return abs_pos


def filter_by_area(detections: List[Dict]) -> List[Dict]:
    # disable
    MIN_AREA_FIRE = 0
    MIN_AREA_PEOPLE = 0

    filtred_detections = []

    for detection in detections:
        if detection["name"] == Objects.PEOPLE:
            if detection["area"] > MIN_AREA_PEOPLE:
                filtred_detections.append(detection)
        else:
            if detection["area"] > MIN_AREA_FIRE:
                filtred_detections.append(detection)
    
    return filtred_detections


def add_finded_objects(objs: List) -> None:
    for obj in objs:
        name = obj["name"].name

        data = {
            "name": name,
            "coordinates": obj["position"],
        }
        
        if name == Objects.PEOPLE.name:
            finded_people.append(data)   
        elif name == Objects.FIRE.name:
            finded_fire.append(data)


# region tests

if __name__ == "__main__":
    if False:
        def create_detections(detections: List):
            return {
                "boxes": detections,
                "image_height": 480,
                "image_width": 640
            }


        def create_detection(name: str, center_x: float, area: float, size_x: float, size_y: float) -> Dict:
            # TODO conf
            return {
                "name": name, 
                "center": { "x": center_x, "y": 0, "theta": 0},
                "area": area, 
                "size_x": size_x, 
                "size_y": size_y 
            }

        alt = 0.5

    if False:
        print(calc_abs_pos([0.32, 2.27], 1.39, 190, 384, 0))

    if False:
        for i in range(10):
            d1 = create_detection("human", 100, 1000, 100, 170)
            d2 = create_detection("human", 500, 500, 100, 200)

            ds = create_detections([d1, d2])

            process_detections(ds, [0, 0], 0)

        sorted_mean_peoples, sorted_mean_fires = get_sorted_detections()
        save_detections(sorted_mean_peoples, sorted_mean_fires)


    if False:
        TARGETS = [[0, 0], [0, 1], [1, 3]]
        add_finded_objects([[Objects.PEOPLE,1,5], [Objects.PEOPLE,2,5.1]])
        add_finded_objects([[Objects.PEOPLE,2,5], [Objects.PEOPLE,4,5.1]])
        add_finded_objects([[Objects.PEOPLE,4,2], [Objects.PEOPLE,5,5.1]])
        add_finded_objects([[Objects.PEOPLE,7,5], [Objects.PEOPLE,6,6.2]])

        mean_finded_people = calc_mean_objects(list(map(lambda peolpe: peolpe["coordinates"], finded_people)))
        mean_finded_fire = calc_mean_objects(list(map(lambda fire: fire["coordinates"], finded_fire)))


        while 1:
            pygame_map.update([0, 0], mean_finded_people, mean_finded_fire)
            pygame_map.route(TARGETS)