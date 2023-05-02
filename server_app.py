#! /usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import asyncio
except ImportError:
    import uasyncio as asyncio
try:
    import json
except ImportError:
    import ujson as json

from iot import server
from local import PORT, TIMEOUT
import struct  # for data stream to float conversion

class App:
    def __init__(self, client_id):
        self.client_id = client_id  # This instance talks to this client
        self.conn = None  # Connection instance
        self.data1 = []  # Start with no data
        self.data2 = []  # Start with no data
        self.data3 = []  # Start with no data
        self.command = {"Code":0}
 
#        file1 = open("Ch1.txt", "a")  # append mode
#        file2 = open("Ch2.txt", "a")  # append mode
#        file3 = open("Ch3.txt", "a")  # append mode

        asyncio.create_task(self.start())

    async def start(self):
        print('Client {} Awaiting connection.'.format(self.client_id))
        self.conn = await server.client_conn(self.client_id)
        asyncio.create_task(self.reader())
        asyncio.create_task(self.writer())

    async def reader(self):
        print('Started reader')
        while True:
            data = await self.conn.read(96)  # Read 96 bytes directly
            if len(data) == 96:
                newData = struct.unpack('12d', data)  # unpack 12 double type data to list
                self.data1.append(newData[0:3])
                self.data2.append(newData[4:7])
                self.data3.append(newData[8:11])
                print('Got', newData, 'from remote', self.client_id)
            else:
                print("Unexpected data length. Skipping unpacking.")
                print('Got', data, 'from remote', self.client_id)


    # Send
    # [approx app uptime in secs/5, received client uptime, received mem_free]
    async def writer(self):
        print('Started writer')
        while True:
            print('Sent', self.command, 'to remote', self.client_id, '\n')
            # .write() behaves as per .readline()
            await self.conn.write(json.dumps(self.command))
            await asyncio.sleep(5)

async def main():
#    clients = {'1', '2', '3', '4'}
#    apps = [App(n) for n in clients]  # Accept 4 clients with ID's 1-4
    clients = {'1'}
    apps = [App(n) for n in clients]  # Use only 1 clients
    await server.run(clients, True, port=PORT, timeout=TIMEOUT)

def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Interrupted')
    finally:
        print('Closing sockets')
        server.Connection.close_all()
        asyncio.new_event_loop()
#        file1.close()
#        file2.close()
#        file3.close()


if __name__ == "__main__":
    run()
