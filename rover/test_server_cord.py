import socket

def start_server(host='127.0.0.1', port=65432):
    """Запуск TCP сервера для приема координат и команд"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Сервер запущен на {host}:{port}")
        
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Подключен клиент: {addr}")
                while True:
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    
                    # Обработка полученных данных
                    try:
                        parts = data.split()
                        if len(parts) < 3:
                            raise ValueError
                            
                        x = float(parts[0])
                        y = float(parts[1])
                        command = parts[2]
                        
                        if command not in ("fire", "human"):
                            raise ValueError
                            
                        print(f"Получены координаты: ({x}, {y}) | Команда: {command}")
                        conn.sendall(b"OK")
                        
                    except ValueError:
                        conn.sendall(b"ERROR")
                        print(f"Ошибка в данных: {data}")

start_server()