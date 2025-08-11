from typing import List

DISTANCE_TRASHOLD = 1


def calc_mean_objects(objects: List[List[float]]) -> List[List[float]]:
    mean_objects = []
    
    for object in objects:
        is_far = True
    
        for ind in range(len(mean_objects) - 1, -1, -1):
            dist = calc_distance(object, mean_objects[ind]['point'])
    
            if dist <= DISTANCE_TRASHOLD:
                is_far = False
                mean_objects[ind]["point"] = calc_mean(mean_objects[ind]["point"], object, mean_objects[ind]["count"])
                mean_objects[ind]["count"] += 1 
                break
    
        if is_far:
            mean_objects.append({"point": object, "count": 1})
    
    return mean_objects


def calc_mean(p1: List[float], p2: List[float], count: int) -> List[float]:
    return [(p1[0]*count + p2[0]) / (count+1), (p1[1]*count + p2[1]) / (count+1)]


def calc_distance(p1: List[float], p2: List[float]) -> float:
    return ((p1[0] - p2[0])**2 + (p2[1] - p1[1])**2)**0.5


def sorted_by_dist(points: List, origin: List=[0, 0]) -> List:
    return sorted(points, key=lambda p: (p[0] - origin[0])**2 + (p[1] - origin[1])**2)
