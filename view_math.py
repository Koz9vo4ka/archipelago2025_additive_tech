from typing import List
from math import radians, tan, sin, cos


def calc_abs_ang(center_x: float, center_y: float, roll: float, pitch: float, h_fov: float, aspect_ratio: float) -> List[float]:
    """
    center_x, center_y - нормированные от 0 до 1
    roll, pitch - продольный и поперечный угол наклона дрона в радианах
    h_fov - угол обзора в горизонте в градусах
    v_fov - угол обзора по вертикали в градусах

    вычисляет углы на объект в глобальной системе координат:
    0) поперечный угол (0 когда объект под дроном) в радианах
    1) продольный угол (0 когда объект под дроном) в радианах
    """
    v_fov = h_fov / aspect_ratio
    a = radians(center_x * h_fov - h_fov / 2)
    b = radians(center_y * v_fov - v_fov / 2)
    
    return [
        a + roll,
        b + pitch
    ]


def calc_local_pos(a: float, b: float, alt: float) -> List[float]:
    """
    a - поперечный угол (0 когда объект под дроном)
    b - продольный угол (0 когда объект под дроном)
    alt - текущая высота полёта в метрах
    
    возвращает положение объекта в локальной системе координат (в системе координат дрона)
    0) расстояние в продольном направлении в метрах
    1) расстояние в поперечном направлении в метрах
    """
    local_x = alt * tan(b)
    local_y = alt * tan(a)
    
    return [local_x, local_y]


def calc_relative_pos(local_x: float, local_y: float, yaw: float) -> List[float]:
    """
    local_x - положение относительно продольной оси дрона
    local_y - положение относительно поперечной оси дрона
    yaw - текущий курс дрона в радианах
    
    возвращает положение обхекта относительно дрона
    0) положение по оси x относительно положения дрона
    1) положение по оси y относительно положение дрона
    """
    relative_x = local_x * cos(yaw) - local_y * sin(yaw)
    relative_y = local_x * sin(yaw) + local_y * cos(yaw)
    
    return [relative_x, relative_y]


def calc_abs_pos(relative_x: float, relative_y: float, current_x: float, current_y: float) -> List[float]:
    """
    relative_x - положение по оси x относительно положения дрона
    relavite_y - положение по оси y относительно положение дрона
    current_x, current_y - положение дрона в глобальное системе координат
    
    возвращает положение обхекта относительно дрона
    0) положение по оси x в глобальной системе координат
    1) положение по оси y в глобальной системе координат
    """
    global_x = relative_x + current_x
    global_y = relative_y + current_y
    
    return [global_x, global_y]
