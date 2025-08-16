"""
Надо чтобы было движение по точкам и при обнаружении новых объектов мы шли обрабатывать их
"""

from drone_control_api.Drone import Drone
from servo_manager import ServoClient

from grock_algoritm import calc_distance
from typing import List
from math import degrees


def calc_angle_error(ang_1: float, ang_2: float) -> float:
    error = abs(ang_1 - ang_2)
    error = min(error, 360 - error)
    return error


class StateMachine:
    def __init__(self, mission:List, client: Drone, target_alt: float) -> None:
        self.__DISTANCE_TRASHOLD_M = 0.5
        self.__YAW_TRASHOLD_DEG = 10
        
        self.__is_above_the_object = False

        self.__targets = mission
        self.__client = client
        self.__servo_client = ServoClient()
        self.__FLOWER_ALT = 0.5
        self.__TARGET_ALT = target_alt
        
        self.__last_alt = None

    def process(self, pose: List[float], rpy: List[float]) -> None:
        self.__horirontal_motion(pose, rpy)
        self.__vertical_motion(pose[2])
    
    def get_flowers_height(self, alt: float) -> float:
        if self.__is_above_the_object:
            return alt
        return alt - self.__FLOWER_ALT
    
    def get_is_above_object(self) -> bool:
        return self.__is_above_the_object
    
    def __horirontal_motion(self, pose: List[float], rpy: List[float]) -> None:
        target = self.__get_target()
        mission_type = len(target)
        if mission_type == 2:  # go to
            is_complete = self.__move_state(pose[:2], target)
        elif mission_type == 1: # rotate
            is_complete = self.__rotate_state(rpy[2], target[0])
        elif mission_type == 0:  # landing
            is_complete = self.__landing_state()
        else:
            is_complete = True
        
        if is_complete:
            self.__next_state()
    
    def __vertical_motion(self, alt: float) -> None:
        """Метод изменяет высоту полета, когда мы пролетаем над цветками

        Args:
            alt (float): текущая высота
        """
        if self.__last_alt is None:
            self.__last_alt = alt
            return
        
        delta_alt = alt - self.__last_alt
        
        if delta_alt < -self.__FLOWER_ALT:  # Оказались ниже на высоту цветка
            if not self.__is_above_the_object:
                self.__set_height_state(self.__TARGET_ALT - self.__FLOWER_ALT)
                # Вызываем drop_corn_to_flower только при переходе из False в True
                if not self.__was_above_the_object:
                    self.__servo_client.drop_corn_to_flower()
                    self.__was_above_the_object = True
            self.__is_above_the_object = True
        elif delta_alt > self.__FLOWER_ALT:
            if self.__is_above_the_object:
                self.__set_height_state(self.__TARGET_ALT)
                self.__was_above_the_object = False
            self.__is_above_the_object = False
    
    def get_mission(self) -> List[List[float]]:
        return self.__targets
    
    def __set_height_state(self, height: float) -> None:
        self.__client.set_height_nb(height)
    
    def is_mission_end(self) -> bool:
        if len(self.__targets) <= 0:
            return True
        return False

    def __move_state(self, current_pos: List[float], target_pos: List[float]) -> bool:
        dist = calc_distance(current_pos, target_pos)

        if dist < self.__DISTANCE_TRASHOLD_M:
            return True
        
        self.__client.go_to_xy_nav_nb(*target_pos)
        print(f"{target_pos=}           {current_pos=}          {dist=}")
        
        return False

    def __rotate_state(self, current_yaw: float, target_yaw: float) -> bool:
        ang_err = calc_angle_error(degrees(current_yaw), target_yaw)

        if ang_err < self.__YAW_TRASHOLD_DEG:
            return True
        
        self.__client.set_yaw_nb(target_yaw)
        print(f"{current_yaw=}           {target_yaw=}          {ang_err=}")
        
        return False

    def __landing_state(self) -> bool:
        self.__client.landing_nb()
        return False

    def __get_target(self) -> List:
        if len(self.__targets) > 0:
            return self.__targets[0]
        return []  # landing
    
    def __next_state(self) -> None:
        if len(self.__targets) > 0:
            self.__targets.pop(0)


if __name__ == "__main__":
    print(StateMachine([[2,4]], Drone(), 1).get_mission())