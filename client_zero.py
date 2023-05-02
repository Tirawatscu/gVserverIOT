# c_app.py Client-side application demo

# Released under the MIT licence. See LICENSE.
# Copyright (C) Peter Hinch 2018-2020

# Now uses and requires uasyncio V3. This is incorporated in daily builds
# and release builds later than V1.12

import asyncio
import socket
import json
from gpiozero import LED

# Optional LED. led=None if not required
led = LED(17)  # Optional LED
# End of optional LED

import local
import ctypes

class App:
    def __init__(self, verbose):
        self.verbose = verbose
        self.conn = None
        self.buf = (ctypes.c_double * 12)()  # Buffer for 12 double precision data   /  3 Ch x 4 Data each / Interleave data
        self.command = None

    async def start(self):
        self.verbose and print('App awaiting connection.')
        await self.connect()
        asyncio.create_task(self.reader())
        await self.writer()

    async def connect(self):
        while self.conn is None:
            try:
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.conn.connect((local.SERVER, local.PORT))
                print("Connection established.")
            except Exception as e:
                print("Connection failed:", e)
                await asyncio.sleep(1)

    async def reader(self):
        self.verbose and print('Started reader')
        while True:
            try:
                # Attempt to read data: in the event of an outage, .recv()
                # pauses until the connection is re-established.
                data = b''
                while b'\n' not in data:
                    data += self.conn.recv(1024)

                line = data.decode('utf-8').rstrip()
                command = json.loads(line)
                # Receives [restart count, uptime in secs]
                self.verbose and print('Got', command , 'from server app')
            except OSError as e:
                print("Error reading data:", e)
                self.conn.close()
                self.conn = None
                await self.connect()

    # Send [approx application uptime in secs, (re)connect count]
    async def writer(self):
        self.verbose and print('Started writer')
        data1 = [1 ,2 ,3 ,4 , 5 ,6 ,7 ,8 , 9 ,10 ,11 ,12 ]  # Three channels x 4 data each = 8 Byts x 3 x 4  = 96 Bytes
        data2 = [10,20,30,40, 50,60,70,80, 90,100,110,120]  # Three channels x 4 data each = 8 Byts x 3 x 4  = 96 Bytes
        bufferFlag = True 
        while True:
            if bufferFlag :
                self.verbose and print('Sent', data1, 'to server app\n')
                self.buf[:]  = data1   # Convert from float to bytes for sending
            else:
                self.verbose and print('Sent', data2, 'to server app\n')
                self.buf[:]  = data2   # Convert from float to bytes for sending
            bufferFlag = not bufferFlag
            # .send() behaves as per .recv()
            self.conn.send(self.buf)
            await asyncio.sleep(0.002) 

    def shutdown(self):
        if self.conn:
            self.conn.close()

app = None
async def main():
    global app  # For finally clause
    app = App(verbose=True)
    await app.start()

try:
    asyncio.run(main())
finally:
    app.shutdown()