from drone_control_api import Drone
import objects_manager as obj_manager 
from motion_manager import StateMachine
import time
import cv2

from drone_pygame_map import DroneDataVisualization()


class DroneMission:
    def __init__(self, drone_ip: str) -> None:  
        self.start_time = time.time()      
        self.__DRONE_IP = drone_ip
        self.result = []
        self.last_time_photo = 0
        
        self.mission_plan = [
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
        ]
        
        self.client = Drone()
        self.pygame_visualization = DroneDataVisualization()
        self.motion_machine = StateMachine(self.mission_plan, self.drone)
        

    def connect_to_drone(self) -> None:
        print(self.drone.connect(self.drone_ip, reset_state=True))

    def taking_off(self, altitude) -> None:
        self.drone.set_height(altitude)
        print(f"TAKE OFF!! set_height = {altitude}")
    
    def process_detections_and_display(self):
        img = self.drone.get_image()
        x, y = self.drone.get_nav_pose()
        yaw = self.drone.get_rpy()[2]

        self.motion_machine.process(x, y, yaw)
        
        obj_manager.process_detections(self.drone.get_detections(), [x, y], yaw)
        peoples, fires = obj_manager.get_sorted_detections()
        self.pygame_visualization.update([x, y, yaw], [], peoples, fires)

        if self.pygame_visualization.get_is_screenshot():
            cv2.imwrite(f"photos/{round(x, 2)}|{round(y, 2)}|{round(yaw, 4)}|{round(time.time(), 3)}.png", img)
        
        cv2.imshow("video", img)
        return x, y, yaw
    
    def check_mission_status(self):
        if self.motion_machine.is_mission_end():
            self.drone.landing_nb()
            print("LANDING!!")
            return False
        return True
    
    def periodic_save_detections(self):
        if abs(self.last_time_photo - time.time()) > 3:
            peoples, fires = obj_manager.get_sorted_detections()
            obj_manager.save_detections(peoples, fires)
            self.last_time_photo = time.time()
    
    def run_mission(self):
        self.connect_to_drone()
        self.taking_off(1.5)
        
        while True:
            self.process_detections_and_display()
            
            if not self.check_mission_status():
                break
                
            self.periodic_save_detections()
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == "__main__":
    mission = DroneMission("192.168.192.38")
    mission.run_mission()
