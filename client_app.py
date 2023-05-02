# c_app.py Client-side application demo

# Released under the MIT licence. See LICENSE.
# Copyright (C) Peter Hinch 2018-2020

# Now uses and requires uasyncio V3. This is incorporated in daily builds
# and release builds later than V1.12

import uasyncio as asyncio
from iot import client
import ujson
# Optional LED. led=None if not required
from sys import platform
from machine import Pin
led = Pin(2, Pin.OUT, value=1)  # Optional LED
# End of optional LED

from . import local
import ctypes

class App(client.Client):
    def __init__(self, verbose):
        self.verbose = verbose
        self.cl = client.Client(local.MY_ID, local.SERVER, local.PORT, local.SSID, local.PW,
                                local.TIMEOUT, conn_cb=self.constate, verbose=verbose,
                                led=led, wdog=False)
        buf = (ctypes.c_double * 12 )()  # Buffer for 12 double precision data   /  3 Ch x 4 Data each / Interleave data
        command = None

    async def start(self):
        self.verbose and print('App awaiting connection.')
        await self.cl
        asyncio.create_task(self.reader())
        await self.writer()

    def constate(self, state):
        print("Connection state:", state)

    async def reader(self):
        self.verbose and print('Started reader')
        while True:
            # Attempt to read data: in the event of an outage, .readline()
            # pauses until the connection is re-established.
            line = await self.cl.readline()
            command = ujson.loads(line)
            # Receives [restart count, uptime in secs]
            self.verbose and print('Got', command , 'from server app')

    # Send [approx application uptime in secs, (re)connect count]
    async def writer(self):
        self.verbose and print('Started writer')
        data1 = [1 ,2 ,3 ,4 , 5 ,6 ,7 ,8 , 9 ,10 ,11 ,12 ]  # Three channels x 4 data each = 8 Byts x 3 x 4  = 96 Bytes
        data2 = [10,20,30,40, 50,60,70,80, 90,100,110,120]  # Three channels x 4 data each = 8 Byts x 3 x 4  = 96 Bytes
        bufferFlag = True 
        while True:
            if bufferFlag :
                self.verbose and print('Sent', data1, 'to server app\n')
                buf[:]  = data1   # Convert from float to bytes for sending
            else:
                self.verbose and print('Sent', data2, 'to server app\n')
                buf[:]  = data2   # Convert from float to bytes for sending
            bufferFlag = not bufferFlag
            # .write() behaves as per .readline()
            await self.cl.write(buf, True, True)
            await asyncio.sleep_ms(2)  # Write every 2 ms  = 

    def shutdown(self):
        self.cl.close()  # Shuts down WDT (but not on Pyboard D).

app = None
async def main():
    global app  # For finally clause
    app = App(verbose=True)
    await app.start()

try:
    asyncio.run(main())
finally:
    app.shutdown()
    asyncio.new_event_loop()
