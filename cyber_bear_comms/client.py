# Tetris_KM/cyber_bear_comms/client.py
import asyncio
import threading
import queue
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"

# ✅ Единый маппинг для обоих мишек (1=вверх, 2=влево, 3=вниз, 4=вправо, 0=отпускание)
BEAR_MAP = {1: 'up', 2: 'left', 3: 'down', 4: 'right', 0: None}


class CyberBearClient:
    def __init__(self, serials=None, max_bears=2):
        self.serials = serials or []
        self.max_bears = max_bears
        self.action_queue = queue.Queue()
        self.status = {'bear1': False, 'bear2': False}
        self._thread = None
        self._loop = None
        self._stop_event = threading.Event()
        self.is_running = False
        self._clients = {}  # Храним активные подключения

    def _make_callback(self, player_num):
        """Фабрика callback-функций с выводом в терминал"""

        def callback(sender, data):
            if len(data) >= 1:
                byte_val = data[0]
                action = BEAR_MAP.get(byte_val, f"Unknown({byte_val})")

                # ✅ Вывод в терминал для отладки
                print(f"🐻 Bear {player_num} | Byte: {byte_val:3d} | Action: {action}")

                if byte_val in BEAR_MAP:
                    try:
                        self.action_queue.put_nowait((player_num, BEAR_MAP[byte_val]))
                    except queue.Full:
                        pass

        return callback

    async def _connect_bear(self, device, bear_num):
        """Подключение одного мишки по логике из Rust-кода"""
        client = BleakClient(device.address)
        try:
            print(f"🔗 Подключение к Мишке {bear_num} ({device.name})...")
            await client.connect()

            # CH9141K workaround: отключаем и подключаем снова
            print(f"🔄 Переподключение Мишки {bear_num}...")
            await client.disconnect()
            await asyncio.sleep(0.3)  # ⚡ Критическая задержка для стабильности
            await client.connect()

            # Запуск уведомлений с привязкой к player_num
            await client.start_notify(NOTIFY_UUID, self._make_callback(bear_num))

            self.status[f'bear{bear_num}'] = True
            self._clients[bear_num] = client
            print(f"✅ Мишка {bear_num} готов!")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения Мишки {bear_num}: {e}")
            return False

    async def _async_task(self):
        try:
            print("🔍 Поиск КиберМишек...")
            devices = await BleakScanner.discover(timeout=5.0)
            found_bears = []

            for dev in devices:
                if dev.name and dev.name.startswith("KM-"):
                    dev_serial = dev.name.replace("KM-", "")
                    if not self.serials or dev_serial in self.serials:
                        found_bears.append(dev)
                        print(f"✅ Найден: {dev.name}")
                        if len(found_bears) >= self.max_bears:
                            break

            if not found_bears:
                print("⚠️ КиберМишки не найдены.")
                return

            # ✅ Последовательное подключение как в Rust
            success_count = 0
            for idx, dev in enumerate(found_bears):
                bear_num = idx + 1
                if await self._connect_bear(dev, bear_num):
                    success_count += 1

            if success_count == 0:
                print("️ Не удалось подключиться ни к одному мишке.")
                return

            print("🎮 Ожидание сигналов...")
            while not self._stop_event.is_set():
                await asyncio.sleep(0.1)

        except Exception as e:
            print(f"🔥 Ошибка BLE сессии: {e}")
        finally:
            print("🔌 Отключение мишек...")
            for num, client in self._clients.items():
                try:
                    if client.is_connected: await client.disconnect()
                except:
                    pass
            self._clients.clear()
            self.is_running = False

    def start(self):
        if self.is_running: return
        self.is_running = True
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_async, daemon=True)
        self._thread.start()

    def _run_async(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._async_task())
        except KeyboardInterrupt:
            pass
        finally:
            self._loop.close(); self.is_running = False

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive(): self._thread.join(timeout=2.0)
        self.is_running = False

    def get_actions(self):
        actions = []
        while not self.action_queue.empty():
            try:
                actions.append(self.action_queue.get_nowait())
            except:
                break
        return actions

    def clear_queue(self):
        """Очищает очередь от старых сигналов"""
        with self.action_queue.mutex:
            self.action_queue.queue.clear()

    def get_status(self):
        return self.status.copy()