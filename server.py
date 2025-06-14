import socket
import threading
import os
import base64
import random
import time

class UDPServer:
    def __init__(self, port):
        self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.welcome_socket.bind(('0.0.0.0', port))
        print(f"The server is running and listening on {port}")


