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
    
    def download_file(self, filename, data_port, file_size):
        print(f"Starting download of file: {filename}, size: {file_size} bytes")
        
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data_socket.settimeout(1) 
        data_address = (self.server_host, data_port)
        
        with open(filename, 'wb') as f:
            downloaded = 0
            block_size = 1000  
            
            while downloaded < file_size:
                start = downloaded
                end = min(downloaded + block_size - 1, file_size - 1)
                
                request = f"FILE {filename} GET START {start} END {end}"
                response = self.send_and_receive(request, data_address)
                
                if response is None:
                    print(f"Error downloading file {filename}, aborting download")
                    data_socket.close()
                    return False
                
                parts = response.split()
                if len(parts) < 9 or parts[0] != "FILE" or parts[1] != filename or parts[2] != "OK":
                    print(f"Received invalid response: {response}")
                    continue
                
                data_index = parts.index("DATA") + 1
                base64_data = " ".join(parts[data_index:])
                
                try:
                    file_data = base64.b64decode(base64_data)
                    f.write(file_data)
                    downloaded += len(file_data)
                    
                    progress = int(downloaded / file_size * 50)
                    print(f"\r[{'>' * progress}{' ' * (50 - progress)}] {downloaded}/{file_size} bytes", end="")
                    
                except Exception as e:
                    print(f"Error processing data: {e}")
                    data_socket.close()
                    return False
            
            print(f"File {filename} download complete, size: {downloaded} bytes")
            
            close_request = f"FILE {filename} CLOSE"
            close_response = self.send_and_receive(close_request, data_address)
            
            if close_response and "CLOSE_OK" in close_response:
                print(f"Received server confirmation to close, file: {filename}")
            else:
                print(f"Did not receive server confirmation to close, file: {filename}")
        
        data_socket.close()
        return True
    


