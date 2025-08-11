import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

points = [[1.8, 455], [2, 440], [2.2, 429], [2.4, 416], [2.6, 405], [2.8, 400], [3, 391], [3.5, 376], [4, 363]]
print(f"POINTS: {points}")

x, y = np.array(list(map(lambda x: x[0], points)), dtype=float), np.array(list(map(lambda x: x[1], points)), dtype=float)
x, y = y, x


def dist_func(value: float, a: float, b: float) -> float:
    return a / value + b

# Fit the exponential function to the data
params, covariance = curve_fit(dist_func, x, y)

# Extract the fitted parameters
a, b = params
print(f"Fitted parameters: a = {a:.2f}, b = {b:.2f} result function is {a:.4f} / x + {b:.4f} = distance")

# Generate fitted y values
y_fit = dist_func(x, a, b)

plt.scatter(x, y, color='blue', label='Исходные точки')  # Исходные точки
plt.plot(x, y_fit, color='red', label='Аппроксимированная функция')  # Аппроксимированная функция
plt.xlabel('width, (px)')
plt.ylabel('distance, (m)')
plt.title('Аппроксимация функции дистанции от center_y рамки по точкам')
plt.legend()
plt.grid(True)
plt.show()