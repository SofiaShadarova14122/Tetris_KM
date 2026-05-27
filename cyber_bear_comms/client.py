# Tetris_KM/cyber_bear_comms/client.py
import asyncio, threading, queue
from bleak import BleakScanner, BleakClient

SVC = "0000fff0-0000-1000-8000-00805f9b34fb"
NOT = "0000fff1-0000-1000-8000-00805f9b34fb"
MAP = {1:'up', 2:'left', 3:'down', 4:'right', 0:None}

class CyberBearClient:
    def __init__(self, serials=None, max_bears=2):
        self.serials = serials or []
        self.max_bears = max_bears
        self.queue = queue.Queue()
        self.status = {'bear1':False, 'bear2':False}
        self._thread = self._loop = None
        self._stop = threading.Event()
        self._running = False
        self._cbs = []

    def _cb(self, num):
        def f(s, d):
            if len(d) and d[0] in MAP:
                try: self.queue.put_nowait((num, MAP[d[0]]))
                except: pass
        self._cbs.append(f)
        return f

    async def _connect(self, dev, num):
        c = BleakClient(dev.address)
        try:
            await c.connect()
            await c.disconnect()
            await asyncio.sleep(0.3)
            await c.connect()
            await c.start_notify(NOT, self._cb(num))
            self.status[f'bear{num}'] = True
            return c
        except Exception as e:
            print(f"❌ Bear {num}: {e}")
            return None

    async def _run(self):
        try:
            devs = await BleakScanner.discover(timeout=5)
            targets = [d for d in devs if d.name and d.name.startswith("KM-")
                      and (not self.serials or d.name[3:] in self.serials)][:self.max_bears]
            clients = []
            for i, d in enumerate(targets):
                c = await self._connect(d, i+1)
                if c: clients.append(c)
            while not self._stop.is_set():
                await asyncio.sleep(0.1)
        finally:
            for c in clients:
                try:
                    if c.is_connected: await c.disconnect()
                except: pass
            self._running = False

    def start(self):
        if self._running: return
        self._running = True
        self._stop.clear()
        self._thread = threading.Thread(target=self._async_main, daemon=True)
        self._thread.start()

    def _async_main(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try: loop.run_until_complete(self._run())
        finally: loop.close()

    def stop(self):
        self._stop.set()
        if self._thread and self._thread.is_alive(): self._thread.join(2)
        self._running = False

    def get_actions(self):
        acts = []
        while not self.queue.empty():
            try: acts.append(self.queue.get_nowait())
            except: break
        return acts

    def clear_queue(self):
        with self.queue.mutex: self.queue.queue.clear()

    def get_status(self): return self.status.copy()