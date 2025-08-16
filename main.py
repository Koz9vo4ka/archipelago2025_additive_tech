from drone_mission import DroneMission

DRONE_IP = '192.168.192.182'
START_ALT = 0.5

drone_control = DroneMission(DRONE_IP,[[1.0, 0.0]], START_ALT)


def main() -> None:
    drone_control.run_mission()


if __name__ == "__main__":
    main()
