"""
Клиент-обёртка с теми же методами, что и NavBot, но работающий через WebSocket.
Использование полностью идентично настоящему API:

    from nav_api_ws import NavBot
    bot = NavBot(host="192.168.0.10")
    ok, dist = bot.check_target(1.0, 0.5)
"""

import asyncio, json, logging, threading, time, uuid
from typing import Any, Dict, List, Tuple, Optional

import websockets

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("NavBotWS")

_WS_TIMEOUT = 3.0            # ожидание ответа
_MAX_RETRIES = 5             # макс. подряд неудачных запросов

class _SyncLoop:
    """Вспомогательный класс: отдельный поток с asyncio-циклом."""

    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        th = threading.Thread(target=self.loop.run_forever, daemon=True)
        th.start()

    def run(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop).result()

class NavBot:
    """Web-socket прокси той же формы, что и настоящий NavBot."""

    def __init__(self, host: str = "localhost", port: int = 8765) -> None:
        self.uri = f"ws://{host}:{port}"
        self._id = 1
        self._fail = 0
        self._sent, self._recv = 0, 0
        self._start = time.time()
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._loop = _SyncLoop()
        self._connect()

    # ---------- соединение ----------
    def _connect(self) -> None:
        # ИСПРАВЛЕНИЕ: создаём корутину для подключения
        async def _async_connect():
            return await websockets.connect(self.uri)
        
        self._ws = self._loop.run(_async_connect())
        log.info("Connected to %s", self.uri)

    # ---------- базовый RPC ----------
    def _rpc(self, payload: Dict[str, Any], CONFIG_TIMEOUT = _WS_TIMEOUT, RETRIES = _MAX_RETRIES) -> Dict[str, Any]:
        """Отправка запроса с авторесендом при потере ответа."""
        if "id" not in payload:          # у первого посыла новый id
            payload["id"] = self._id
            self._id += 1

        for attempt in range(RETRIES):
            try:
                # ИСПРАВЛЕНИЕ: создаём корутины для отправки и получения
                async def _send_and_recv():
                    await self._ws.send(json.dumps(payload))
                    return await asyncio.wait_for(self._ws.recv(), timeout=CONFIG_TIMEOUT)
                
                result = self._loop.run(_send_and_recv())
                self._sent += 1
                self._recv += 1
                self._fail = 0
                return json.loads(result)
            except Exception:
                self._fail += 1
                log.warning("No reply (%s/%s)", attempt + 1, RETRIES)
                if self._fail >= RETRIES:
                    raise ConnectionError("server unreachable") from None
                # повторяем с тем же id
                time.sleep(0.2)
                # при разрыве пытаемся пересоздать соединение
                try:
                    if self._ws.closed:
                        self._connect()
                except Exception:
                    pass
        raise TimeoutError("request timeout")

    # ---------- метрики ----------
    def stats(self) -> Dict[str, float]:
        return {
            "sent": self._sent,
            "received": self._recv,
            "cps": self._sent / max(1e-3, time.time() - self._start),
        }

    # ------------------------------------------------------------------
    # Ниже повторяются все публичные методы настоящего NavBot.
    # ------------------------------------------------------------------
    def wait_until_ready(self, timeout: float | None = None) -> None:
        self._rpc({"operation": "wait_until_ready", "timeout": timeout})

    def get_pose(self) -> Tuple[float, float, float]:
        r = self._rpc({"operation": "get_pose"})
        return r["x"], r["y"], r["yaw"]

    def check_target(self, x: float, y: float) -> Tuple[bool, float]:
        r = self._rpc({"operation": "check_target", "x": x, "y": y})
        return r["available"], r["distance"]

    def check_around(self) -> List[float]:
        return self._rpc({"operation": "check_around"})["distances"]

    def navigate(self, x: float, y: float, yaw: float = 0.0) -> None:
        self._rpc({"operation": "navigate", "x": x, "y": y, "yaw": yaw})

    def navigate_path(self,
                      waypoints: List[Tuple[float, float, float]]) -> None:
        self._rpc({"operation": "navigate_path", "waypoints": waypoints})

    def point_reached(self) -> int:
        return self._rpc({"operation": "point_reached"})["status"]

    def path_len(self) -> float:
        return self._rpc({"operation": "path_len"})["length"]

    def save_map(self, name: str) -> None:
        self._rpc({"operation": "save_map", "name": name})

    def load_map(self, name: str,
                 pose: Optional[Tuple[float, float, float]] = None) -> None:
        self._rpc({"operation": "load_map", "name": name, "pose": pose})

    def joy_button(self, button_name: str) -> bool:
        return self._rpc({"operation": "joy_button",
                          "button_name": button_name})["pressed"]

    def joy_axis(self, axis_name: str) -> float:
        return self._rpc({"operation": "joy_axis",
                          "axis_name": axis_name})["value"]
    
    def grip(self) -> None:
        self._rpc({"operation": "grip", "data": True}, 8.0, 2)
        # Блокируем локально, чтобы дать время выполнения на стороне сервера
        time.sleep(8.0)

    def rize(self) -> None:
        self._rpc({"operation": "rize", "data": False}, 8.0, 2)
        time.sleep(8.0)