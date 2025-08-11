from grock_algoritm import calc_distance
from typing import List, Tuple
from math import degrees
import math


def calc_angle_error(ang_1: float, ang_2: float) -> float:
    error = abs(ang_1 - ang_2)
    error = min(error, 360 - error)
    return error


class StateMachine:
    def __init__(self, mission, client):
        self.__DISTANCE_TRASHOLD_M = 0.55
        self.__YAW_TRASHOLD_DEG = 10

        self.__targets = mission
        self.__client = client

    def process(self, x: float, y: float, yaw: float) -> None:
        target = self.__get_target()
        mission_type = len(target)
        if mission_type == 2:  # go to
            is_complete = self.__move_state([x, y], target)
        elif mission_type == 1: # rotate
            is_complete = self.__rotate_state(yaw, target[0])
        elif mission_type == 0:  # landing
            is_complete = self.__landing_state()
        else:
            is_complete = True
        
        if is_complete:
            self.__next_state()
    
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
        # NOT TESTED
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


    def __calculate_yaw(robot_x, robot_y, object_x, object_y):
        dx = object_x - robot_x
        dy = object_y - robot_y
        yaw = math.atan2(dy, dx)
        return yaw  # в радианах


if __name__ == "__main__":
    pass