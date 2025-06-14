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

    def send_and_receive(self, message, address, max_retries=5):
        current_timeout = 1  
        retries = 0
        
        while retries <= max_retries:
            try:
                self.client_socket.sendto(message.encode(), address)
                print(f"has sent: {message} to {address}")
                
                response, _ = self.client_socket.recvfrom(4096)
                response_str = response.decode().strip()
                print(f"has accepted: {response_str}")
                return response_str
                
            except socket.timeout:
                retries += 1
                current_timeout *= 2  
                self.client_socket.settimeout(current_timeout)
                print(f"timeout {retries}/{max_retries}， time : {current_timeout}秒")
                if retries > max_retries:
                    print(f"Max retry attempts reached, aborting request.: {message}")
                    return None
    
