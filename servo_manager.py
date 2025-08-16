import socket
from typing import Tuple, Optional
import time

class ServoClient:
    def __init__(self, host: str = "192.168.192.182", port: int = 65432) -> None:
        """
        Инициализация клиента для управления сервоприводом
        
        :param host: IP-адрес Orange Pi (по умолчанию 192.168.182.182)
        :param port: Порт сервера (по умолчанию 65432)
        """
        self.host: str = host
        self.port: int = port
        
    def _send_command(self, angle: int) -> Optional[str]:
        """
        Внутренний метод для отправки команды на сервер
        
        :param angle: Угол поворота сервопривода (0-180)
        :return: Ответ сервера или None при ошибке
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(3.0)  # Таймаут 3 секунды
                s.connect((self.host, self.port))
                s.sendall(str(angle).encode())
                return s.recv(1024).decode()
            except ConnectionRefusedError:
                print("Ошибка: Не удалось подключиться к серверу")
            except socket.timeout:
                print("Ошибка: Превышено время ожидания ответа")
            except Exception as e:
                print(f"Ошибка соединения: {e}")
            return None
    
    def open_servo(self) -> None:
        """Открыть сервопривод (установить угол 0°)"""
        if response := self._send_command(0):
            print(f"Сервопривод открыт. Ответ сервера: {response}")
    
    def close_servo(self) -> None:
        """Закрыть сервопривод (установить угол 90°)"""
        if response := self._send_command(90):
            print(f"Сервопривод закрыт. Ответ сервера: {response}")
    
    def set_angle(self, angle: int) -> None:
        """
        Установить произвольный угол сервопривода
        
        :param angle: Угол поворота (0-180°)
        """
        if not 0 <= angle <= 180:
            print("Ошибка: Угол должен быть в диапазоне 0-180°")
            return
            
        if response := self._send_command(angle):
            print(f"Установлен угол {angle}°. Ответ сервера: {response}")
    
    def drop_corn_to_flower(self) -> None:
        client.open_servo()
        time.sleep(1)
        client.close_servo()

if __name__ == "__main__":
    # Создаем клиент с настройками по умолчанию
    client = ServoClient()
    
    try:
        client.open_servo()
        time.sleep(2)
        client.close_servo()
    except KeyboardInterrupt:
        print("\nПрограмма завершена")