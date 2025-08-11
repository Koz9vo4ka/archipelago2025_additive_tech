import socket

def send_data(host='127.0.0.1', port=65432):
    """Клиент для отправки координат и команд"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Подключен к серверу {host}:{port}")
        
        # Предопределенный набор данных
        data_set = [
            (1.23, 4.56, "fire"),
            (7.89, 0.12, "human"),
            (3.45, 6.78, "fire"),
            (9.01, 2.34, "human")
        ]
        
        while True:
            user_input = input("Введите координаты и команду (x y fire/human) или 'all': ")
            
            if user_input.lower() == 'all':
                # Отправка всего набора данных
                for x, y, cmd in data_set:
                    _send(s, x, y, cmd)
                print("Все данные отправлены")
                break
                
            elif user_input.lower() == 'exit':
                break
                
            else:
                # Отправка единичных данных
                try:
                    parts = user_input.split()
                    if len(parts) < 3:
                        raise ValueError
                        
                    x = float(parts[0])
                    y = float(parts[1])
                    cmd = parts[2]
                    _send(s, x, y, cmd)
                    
                except ValueError:
                    print("Ошибка формата! Используйте: <число> <число> fire|human")

def _send(sock, x, y, command):
    """Внутренняя функция отправки данных"""
    data_str = f"{x} {y} {command}"
    sock.sendall(data_str.encode())
    response = sock.recv(1024).decode()
    print(f"Ответ сервера: {response}")

if __name__ == "__main__":
    send_data()