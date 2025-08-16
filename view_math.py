from typing import List
from math import radians, tan, sin, cos


def calc_abs_ang(center_x: float, center_y: float, roll: float, pitch: float, h_fov: float, aspect_ratio: float) -> List[float]:
    """
    :param: center_x (float):
    :param: center_y (float): - нормированные от 0 до 1
    :param: roll (float):
    :param: pitch (float): - продольный и поперечный угол наклона дрона в радианах
    :param: h_fov (float): - угол обзора в горизонте в градусах
    :param: v_fov (float): - угол обзора по вертикали в градусах

    :return: вычисляет углы на объект в глобальной системе координат:
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
    
    :param a (float):  - поперечный угол (0 когда объект под дроном)
    :param b (float): - продольный угол (0 когда объект под дроном)
    :param alt (float): - текущая высота полёта в метрах
    
    :rerturn: возвращает положение объекта в локальной системе координат (в системе координат дрона)
    0) расстояние в продольном направлении в метрах
    1) расстояние в поперечном направлении в метрах
    """
    local_x = alt * tan(b)
    local_y = alt * tan(a)
    
    return [local_x, local_y]


def calc_relative_pos(local_x: float, local_y: float, yaw: float) -> List[float]:
    """
    :param local_x (float): - положение относительно продольной оси дрона
    :param local_y (float): - положение относительно поперечной оси дрона
    :param yaw (float):- текущий курс дрона в радианах
    
    :rerturn: возвращает положение обхекта относительно дрона
    0) положение по оси x относительно положения дрона
    1) положение по оси y относительно положение дрона
    """
    relative_x = local_x * cos(yaw) - local_y * sin(yaw)
    relative_y = local_x * sin(yaw) + local_y * cos(yaw)
    
    return [relative_x, relative_y]


def calc_abs_pos(relative_x: float, relative_y: float, current_x: float, current_y: float) -> List[float]:
    """
    :param relative_x (float): - положение по оси x относительно положения дрона
    :param relavite_y (float): - положение по оси y относительно положение дрона
    :param current_x (float):
    :param current_y (float): - положение дрона в глобальное системе координат
    
    :return: возвращает положение обхекта относительно дрона
    0) положение по оси x в глобальной системе координат
    1) положение по оси y в глобальной системе координат
    """
    global_x = relative_x + current_x
    global_y = relative_y + current_y
    
    return [global_x, global_y]
