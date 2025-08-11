from drone_control_api import Drone
from objects_manager import process_detections, save_detections, get_sorted_detections
from motion_manager import StateMachine
import time
import cv2

import pygame_map

IP_DRONE = "192.168.192.38"

alt = 0.7

result = []

client = Drone()

mission_no_rotation = [
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
    
print(client.connect(IP_DRONE, reset_state=True))

last_time_photo = 0

client.set_height(alt)
print(f"TAKE OFF!! set_height = {alt}")

motion_machine = StateMachine(mission_no_rotation, client)

start_time = time.time()

while True:
    img = client.get_image()
    x, y = client.get_nav_pose()
    yaw = client.get_rpy()[2]

    motion_machine.process(x, y, yaw)
    
    process_detections(client.get_detections(), [x, y], yaw)
    peoples, fires = get_sorted_detections()
    pygame_map.update([x, y, yaw], [], peoples, fires)

    if pygame_map.get_is_screenshot():
        cv2.imwrite(f"photos/{round(x, 2)}|{round(y, 2)}|{round(yaw, 4)}|{round(time.time(), 3)}.png", img)
    cv2.imshow(f"video", img)
    
    if motion_machine.is_mission_end():
        client.landing_nb()
        print("LANDING!!")
        
    if abs(last_time_photo - time.time()) > 3:
        peoples, fires = get_sorted_detections()
        peoples, fires = peoples, fires

        save_detections(peoples, fires)
        last_time_photo = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        pass
