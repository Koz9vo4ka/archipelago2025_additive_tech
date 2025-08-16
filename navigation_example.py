from drone_control_api.Drone import Drone
import datetime
import cv2
import time


def cb(msg):
    global break_flag
    break_flag = True


ip = "192.168.192.182"

result = []


client = Drone()

print(client.connect(ip))

break_flag = False

# client.go_to_xy_nav_nb(2.5, 8.5, callback=cb)


while not break_flag:
    
    img = client.get_image()
    print(client.get_rpy())
    cv2.imshow('ewretry', img)

print(result)

print(client.landing())

print(client.disconnect())



