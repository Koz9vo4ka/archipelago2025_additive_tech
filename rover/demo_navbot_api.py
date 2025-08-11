"""
Демо-скрипт с улучшенной обработкой ошибок и задержками
- Добавлены повторные попытки для критических операций
- Увеличены таймауты
- Улучшена обработка исключений
"""

import time
from rf_bot_api import NavBot

def safe_operation(operation, max_retries=3, delay=1.0, *args, **kwargs):
    """Выполняет операцию с повторными попытками"""
    for attempt in range(max_retries):
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            print(f"Попытка {attempt+1}/{max_retries} не удалась: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                raise

def main():
    print("Инициализация клиента...")
    
    # Подключение с повторными попытками
    bot = safe_operation(NavBot, host="localhost", port=8765)
    print("✓ Соединение установлено")
    
    # Добавляем задержку для инициализации сервера
    time.sleep(1.0)
    
    try:
        # Тест готовности системы
        print("\n1. Проверка готовности системы...")
        safe_operation(bot.wait_until_ready)
        print("✓ Система готова")
        
        # Тест получения позиции
        print("\n2. Получение позиции робота:")
        x, y, yaw = safe_operation(bot.get_pose)
        print(f"   Позиция: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}")
        
        # Тест проверки цели
        print("\n3. Проверка цели (x=1.0, y=2.0):")
        available, distance = safe_operation(bot.check_target, x=1.0, y=2.0)
        print(f"   Доступность: {'Да' if available else 'Нет'}, Дистанция: {distance:.2f}")
        
        # Тест сканирования
        print("\n4. Сканирование окружения:")
        distances = safe_operation(bot.check_around)
        print(f"   Дистанции: {', '.join(f'{d:.2f}' for d in distances)}")
        
        # Тест навигации
        print("\n5. Навигация к точке (x=1.5, y=1.5):")
        safe_operation(bot.navigate, x=1.5, y=1.5)
        
        # Проверка статуса достижения
        print("   Ожидание завершения навигации...")
        for i in range(5):
            try:
                status = bot.point_reached()
                print(f"   Статус: {['В пути', 'Достигнута'][status]}")
                if status == 1:
                    break
            except Exception as e:
                print(f"   Ошибка проверки статуса: {e}")
            time.sleep(1)
        
        # Тест пути
        print("\n6. Навигация по маршруту:")
        path = [(1.0, 1.0, 0.0), (2.0, 2.0, 1.57), (3.0, 3.0, 0.0)]
        safe_operation(bot.navigate_path, waypoints=path)
        
        # Проверка длины пути
        try:
            length = bot.path_len()
            print(f"   Длина маршрута: {length:.2f} м")
        except Exception as e:
            print(f"   Ошибка получения длины: {e}")
        
        # Тест карт
        print("\n7. Работа с картами:")
        safe_operation(bot.save_map, name="test_map")
        safe_operation(bot.load_map, name="test_map", pose=(0.0, 0.0, 0.0))
        print("✓ Операции с картами выполнены")
        
        # Тест джойстика
        print("\n8. Эмуляция джойстика:")
        print(f"   Кнопка A: {'Нажата' if safe_operation(bot.joy_button, button_name='A') else 'Отпущена'}")
        print(f"   Ось LT: {safe_operation(bot.joy_axis, axis_name='LT'):.2f}")
        
        # Тест манипулятора
        print("\n9. Тест манипулятора:")
        print("   Захват...")
        safe_operation(bot.grip)
        print("   Подъем...")
        safe_operation(bot.rize)
        print("✓ Операции с манипулятором выполнены")
        
        # Статистика
        stats = bot.stats()
        print("\nСтатистика работы:")
        print(f"  Отправлено запросов: {stats['sent']}")
        print(f"  Получено ответов: {stats['received']}")
        print(f"  Запросов в секунду: {stats['cps']:.2f}")
        
    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        print("Проверьте подключение и состояние сервера")

if __name__ == "__main__":
    main()