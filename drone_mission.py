from drone_control_api.Drone import Drone

from drone_pygame_map import DroneDataVisualization
from motion_manager import StateMachine
from objects_manager import ObjectManager

from typing import List

import time
import cv2


class DroneMission:
    def __init__(self, drone_ip: str, mission_plan: List, target_alt: float) -> None:
        """
        :param drone_ip: IP адрес OrangePi
        :param mission_plan: Маршут по которым движется дрон
        :param target_alt: Текущая высота дрона
        """
        self.__DRONE_IP = drone_ip
        self.__TARGET_ALT = target_alt

        self.__client = Drone()
        self.__pygame_visualization = DroneDataVisualization()
        self.__motion_machine = StateMachine(mission_plan, self.__client, self.__TARGET_ALT)
        self.__obj = ObjectManager()

    def __connect_to_drone(self) -> None:
        print(self.__client.connect(self.__DRONE_IP, reset_state=True))

    def __taking_off(self, altitude: float) -> None:
        print(f"START TAKE OFF!! set_height = {altitude}")
        self.__client.set_height(altitude)
        print(f"TAKE OFF!!")
    
    def __drop_corn(self):
        pass
    
    def __update(self) -> None:
        self.__check_is_mission_running()
        
        pose, rpy, img = self.__get_data()

        self.__motion_machine.process(pose, rpy)
        mission = self.__motion_machine.get_mission()
        
        flowers_alt = self.__motion_machine.get_flowers_height(pose[2])
        # self.__obj.process_detections(self.__client.get_detections(), [*pose[:2], flowers_alt], rpy)
        objects = self.__obj.get_sorted_detections()
        
        self.__pygame_visualization.update([*pose[:2], rpy[2]], mission, objects)

        if self.__pygame_visualization.get_is_screenshot():
            cv2.imwrite(f"photos/{pose[0]:2f}|{pose[1]:2f}|{pose[2]:2f}|||||{rpy[0]:2f}|{rpy[1]:2f}|{rpy[2]:2f}.png", img)
        
        cv2.imshow("video", img)
    
    def __check_is_mission_running(self) -> bool:
        if self.__motion_machine.is_mission_end():
            self.__client.landing_nb()
            print("LANDING!!")
            return False
        return True
    
    def __get_data(self):
        img = self.__client.get_image()
        pose = self.__client.get_odom_opticflow()
        rpy = self.__client.get_rpy()
        
        if not isinstance(pose, list) and len(pose) == 3:
            print(f"wrong pose: {pose}")
        if not isinstance(rpy, list) and len(rpy) == 3:
            print(f"wrong rpy: {rpy}")
        
        return pose, rpy, img

    def run_mission(self) -> None:
        self.__connect_to_drone()
        self.__taking_off(self.__TARGET_ALT)
        
        while True:
            self.__update()


if __name__ == "__main__":
    mission = DroneMission("192.168.192.38",
        [
            # go forward and back
            [4.0, 0.0],
            [0.5, 0.0],
            # go left
            [0.5, 3.0],
            # go forward to big room
            [2.0, 3.0],
            # go left in big room
            [2.0, 5.5],
            # go to tupic
            [0.0, 5.5],
            # go back to big room
            [1.75, 5.5],
            [1.75, 3.0],
            # go to start
            [0.5, 3.0],
            [0.5, 0.0],
            [0.0, 0.0],
            [],
        ], 1.5)
    mission.run_mission()
