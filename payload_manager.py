import socket
import json
from typing import Dict


class PayloadManager:
    def __init__(self, host: str) -> None:
        """
        Инициализация менеджера полезной нагрузки для TCP-соединения
        
        :param host: IP-адрес или доменное имя сервера
        :param port: Порт сервера
        """
        self.host = host
        self.port = 80
        self.socket = None

    def connect(self) -> bool:
        """
        Установка соединения с сервером
        
        :return: True если соединение установлено, False в противном случае
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except (socket.error, ConnectionRefusedError) as e:
            print(f"Connection error: {e}")
            return False

    def send_payload(self, payload: Dict) -> bool:
        """
        Отправка полезной нагрузки на сервер
        
        :param payload: Данные для отправки (словарь)
        :return: True если отправка прошла успешно, False в противном случае
        """
        if not self.socket:
            print("Not connected to server!")
            return False

        try:
            # Преобразуем словарь в JSON-строку и отправляем
            json_payload = json.dumps(payload).encode('utf-8')
            self.socket.sendall(json_payload)
            return True
        except (socket.error, TypeError) as e:
            print(f"Error sending payload: {e}")
            return False

    def disconnect(self) -> None:
        """Закрытие соединения"""
        if self.socket:
            self.socket.close()
            self.socket = None

# Пример использования
if __name__ == "__main__":
    # Конфигурация подключения
    SERVER_HOST = "127.0.0.1"  # Локальный хост для примера

    # Создаем полезную нагрузку
    payload_data = {
        "command": "drop"
    }
    manager = PayloadManager(SERVER_HOST)
    manager.connect()
    
    # Используем контекстный менеджер для автоматического управления соединением
    print(manager.send_payload(payload_data))
    