"""
Исправленный тестовый WebSocket-сервер для NavBot API.
- Добавлена задержка при запуске
- Улучшена обработка подключений
- Оптимизирована работа с асинхронными операциями
"""

import asyncio
import websockets
import json
import random
import time

class RobotState:
    def __init__(self):
        self.pose = (0.0, 0.0, 0.0)
        self.target_reached = True
        self.path_length = 0.0
        self.ready = True

robot_state = RobotState()

async def handle_operation(data):
    """Обработка операций с гарантированным ответом"""
    operation = data.get("operation")
    response = {"id": data.get("id", 1)}
    
    try:
        if operation == "get_pose":
            response.update({
                "x": robot_state.pose[0],
                "y": robot_state.pose[1],
                "yaw": robot_state.pose[2]
            })
        
        elif operation == "check_target":
            response.update({
                "available": True,
                "distance": random.uniform(0.1, 5.0)
            })
        
        elif operation == "check_around":
            response["distances"] = [random.uniform(0.1, 3.0) for _ in range(8)]
        
        elif operation == "navigate":
            robot_state.pose = (data["x"], data["y"], data.get("yaw", 0.0))
            robot_state.target_reached = False
            response["result"] = "Navigation started"
        
        elif operation == "navigate_path":
            waypoints = data["waypoints"]
            robot_state.path_length = sum( ((waypoints[i][0] - waypoints[i-1][0])**2 +  (waypoints[i][1] - waypoints[i-1][1])**2)**0.5 for i in range(1, len(waypoints)))
            robot_state.target_reached = False
            response["result"] = "Path navigation started"
        
        elif operation == "point_reached":
            # Через 1 секунду отмечаем достижение цели
            if not robot_state.target_reached:
                robot_state.target_reached = time.time() > (data.get("start_time", 0) + 1.0)
            response["status"] = 1 if robot_state.target_reached else 0
        
        elif operation == "path_len":
            response["length"] = robot_state.path_length
        
        elif operation == "wait_until_ready":
            response["result"] = "Ready"
        
        elif operation == "save_map":
            response["result"] = f"Map {data['name']} saved"
        
        elif operation == "load_map":
            response["result"] = f"Map {data['name']} loaded"
        
        elif operation == "joy_button":
            response["pressed"] = random.choice([True, False])
        
        elif operation == "joy_axis":
            response["value"] = random.uniform(-1.0, 1.0)
        
        elif operation == "grip" or operation == "rize":
            response["result"] = "Operation completed"
        
        else:
            response["error"] = f"Unknown operation: {operation}"
    
    except Exception as e:
        response["error"] = f"Server error: {str(e)}"
    
    return response

async def client_handler(websocket):
    """Обработчик клиента с улучшенной стабильностью"""
    print("Клиент подключен")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"Получен запрос: {data}")
                
                # Добавляем временную метку для операций навигации
                if data.get("operation") in ["navigate", "navigate_path"]:
                    data["start_time"] = time.time()
                
                response = await handle_operation(data)
                await websocket.send(json.dumps(response))
                print(f"Отправлен ответ: {response}")
            
            except json.JSONDecodeError:
                error = {"error": "Invalid JSON format"}
                await websocket.send(json.dumps(error))
    except websockets.exceptions.ConnectionClosed:
        print("Клиент отключен")

async def main():
    """Запуск сервера с задержкой перед началом работы"""
    print("Инициализация сервера...")
    await asyncio.sleep(1)  # Критически важная задержка для инициализации
    
    
    host = "127.0.0.1"
    port = 8765
    async with websockets.serve(client_handler, host, port, ping_interval=None):
        print(f"Сервер запущен: ws://{host}:{port}")
        print("Готов к работе")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())