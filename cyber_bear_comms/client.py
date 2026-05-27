# Tetris_KM/cyber_bear_comms/client.py
import asyncio
import threading
import queue
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
NOTIFY_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"

# ✅ Исправленный маппинг (0 вместо 00 для совместимости)
BEAR1_MAP = {1: 'up', 2: 'left', 3: 'down', 4: 'right', 0: None}
BEAR2_MAP = {11: 'up', 22: 'left', 33: 'down', 44: 'right', 0: None}


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
        self._last_sent = {1: None, 2: None}  # Защита от дубликатов

    def _notification_callback(self, sender, data):
        if len(data) >= 1:
            byte_val = data[0]
            player_num, action = None, None

            if byte_val in BEAR1_MAP:
                player_num, action = 1, BEAR1_MAP[byte_val]
            elif byte_val in BEAR2_MAP:
                player_num, action = 2, BEAR2_MAP[byte_val]

            if player_num is not None:
                # ✅ Фильтр дубликатов: отправляем в игру только если состояние изменилось
                if action != self._last_sent[player_num]:
                    self._last_sent[player_num] = action
                    try:
                        self.action_queue.put_nowait((player_num, action))
                    except queue.Full:
                        pass

    async def _async_task(self):
        try:
            print(" Поиск КиберМишек...")
            devices = await BleakScanner.discover(timeout=5.0)
            target_devices = []
            for dev in devices:
                if dev.name and dev.name.startswith("KM-"):
                    dev_serial = dev.name.replace("KM-", "")
                    if not self.serials or dev_serial in self.serials:
                        if dev not in target_devices:
                            target_devices.append(dev)
                            print(f"✅ Найден: {dev.name}")
                            if len(target_devices) >= self.max_bears:
                                break
            if not target_devices:
                print("⚠️ КиберМишки не найдены.")
                return

            for idx, dev in enumerate(target_devices):
                bear_num = idx + 1
                client = BleakClient(dev.address)
                try:
                    await client.connect()
                    await client.disconnect()
                    await client.connect()
                    await client.start_notify(NOTIFY_UUID, self._notification_callback)
                    self.status[f'bear{bear_num}'] = True
                    print(f"🐻 Подключено к мишке {bear_num} ({dev.name})")
                except Exception as e:
                    print(f"❌ Ошибка подключения мишки {bear_num}: {e}")

            print("🎮 Ожидание сигналов от контроллеров...")
            while not self._stop_event.is_set():
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"🔥 Ошибка BLE сессии: {e}")
        finally:
            print("🔌 BLE сессия завершена.")

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
            self._loop.close()
            self.is_running = False

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self.is_running = False

    def get_actions(self):
        actions = []
        while not self.action_queue.empty():
            try:
                actions.append(self.action_queue.get_nowait())
            except queue.Empty:
                break
        return actions

    def get_status(self):
        return self.status.copy()