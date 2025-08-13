from drone_control_api import Drone

from drone_pygame_map import DroneDataVisualization
from motion_manager import StateMachine
from objects_manager import ObjectManager

from typing import List

import time
import cv2


class DroneMission:
    def __init__(self, drone_ip: str, mission_plan: List) -> None:  
        self.__start_time = time.time()      
        self.__DRONE_IP = drone_ip
        self.__last_time_photo = 0
        self.__result = []
        
        self.__mission_plan = mission_plan
        
        self.__client = Drone()
        self.__pygame_visualization = DroneDataVisualization()
        self.__motion_machine = StateMachine(self.__mission_plan, self.__client)
        self.__obj = ObjectManager()
        

    def __connect_to_drone(self) -> None:
        print(self.__client.connect(self.__DRONE_IP, reset_state=True))

    def __taking_off(self, altitude: float) -> None:
        self.__client.set_height(altitude)
        print(f"TAKE OFF!! set_height = {altitude}")
    
    def __process_detections_and_display(self) -> None:
        img = self.__client.get_image()
        x, y = self.__client.get_nav_pose()
        yaw = self.__client.get_rpy()[2]

        self.__motion_machine.process(x, y, yaw)
        
        self.__obj.process_detections(self.__client.get_detections(), [x, y], yaw)
        objects = self.__obj.get_sorted_detections()
        self.__pygame_visualization.update([x, y, yaw], self.__mission_plan, objects)

        if self.__pygame_visualization.get_is_screenshot():
            cv2.imwrite(f"photos/{round(x, 2)}|{round(y, 2)}|{round(yaw, 4)}|{round(time.time(), 3)}.png", img)
        
        cv2.imshow("video", img)
    
    def __check_mission_status(self) -> bool:
        if self.__motion_machine.is_mission_end():
            self.__client.landing_nb()
            print("LANDING!!")
            return False
        return True
    
    def run_mission(self) -> None:
        self.__connect_to_drone()
        self.__taking_off(1.5)
        
        while True:
            self.__process_detections_and_display()
            
            if not self.__check_mission_status():
                break
                
            self.__periodic_save_detections()
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


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
        ])
    mission.run_mission()
