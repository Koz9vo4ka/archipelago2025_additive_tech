from drone_mission import DroneMission

DRONE_IP = '192.168.192.182'
START_ALT = 1.5

drone_control = DroneMission(DRONE_IP,[0.3,3], START_ALT)


def main() -> None:
    drone_control.run_mission()


if __name__ == "__main__":
    main()
