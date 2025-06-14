import socket
import threading
import os
import base64
import random
import time

class UDPServer:
    def __init__(self, port):
        self.server_port = port
        self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.welcome_socket.bind(('0.0.0.0', port))
        print(f"Server started, listening on port {port}")
    
    def start(self):
        try:
            while True:
                request_packet, client_address = self.welcome_socket.recvfrom(1024)
                client_request = request_packet.decode().strip()
                print(f"Request received from {client_address}: {client_request}")
                
                self.handle_download_request(client_request, client_address)
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.welcome_socket.close()
    




