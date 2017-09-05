#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 15:28:57 2017

@author: lukanen
"""

import asyncio

class EchoServerClientProtocol(asyncio.Protocol):
    
    def __init__(self):
        self.count = 0
        
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        global number
        number += 1
        self.count += 1
        print ('number : ', number)
        print ('self.count : ', self.count)
        
    def data_received(self, data):
        message = data.decode()
        print('Data received: {!r}'.format(message))
        
        print('Send: {!r}'.format(message))
        self.transport.write(data)
        
        print('Close the client socket')
        self.transport.close()
        
number = 0
loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(EchoServerClientProtocol, '127.0.0.1', 8888)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()