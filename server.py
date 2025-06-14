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
    
    def handle_download_request(self, request, client_address):
        parts = request.split()
        if len(parts) < 2 or parts[0] != "DOWNLOAD":
            print("Invalid download request")
            return
        
        filename = parts[1]
        file_path = filename
        
        if not os.path.exists(file_path):
            error_response = f"ERR {filename} NOT_FOUND"
            self.welcome_socket.sendto(error_response.encode(), client_address)
            print(f"File {filename} not found, sent error response to client")
            return
        
        file_size = os.path.getsize(file_path)
        data_port = self.choose_data_port()
        
        ok_response = f"OK {filename} SIZE {file_size} PORT {data_port}"
        self.welcome_socket.sendto(ok_response.encode(), client_address)
        print(f"Sent OK response to client, file: {filename}, size: {file_size}, data port: {data_port}")
        
        thread = threading.Thread(
            target=self.handle_file_transmission,
            args=(filename, client_address, data_port)
        )
        thread.daemon = True
        thread.start()
    
    def choose_data_port(self):
        return random.randint(50000, 51000)
    



