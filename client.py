import socket
import base64
import os
import time

class UDPClient:
    def __init__(self, server_host, server_port, file_list):
        self.server_host = server_host
        self.server_port = server_port
        self.file_list = file_list
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(1) 
        print(f"Client initialized, connecting to {server_host}:{server_port}")
    
    def send_and_receive(self, message, address, max_retries=5):
        """Send a message and receive a response with retry mechanism"""
        current_timeout = 1  
        retries = 0
        
        while retries <= max_retries:
            try:
                self.client_socket.sendto(message.encode(), address)
                print(f"Sent: {message} to {address}")
                
                response, _ = self.client_socket.recvfrom(4096)
                response_str = response.decode().strip()
                print(f"Received: {response_str}")
                return response_str
                
            except socket.timeout:
                retries += 1
                current_timeout *= 2  
                self.client_socket.settimeout(current_timeout)
                print(f"Timeout, retrying {retries}/{max_retries}, timeout: {current_timeout} seconds")
                if retries > max_retries:
                    print(f"Max retries reached, giving up on request: {message}")
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
    
    def run(self):
        """Run the client to download all files in the list"""
        server_address = (self.server_host, self.server_port)
        
        try:
            with open(self.file_list, 'r') as f:
                filenames = [line.strip() for line in f if line.strip()]
            
            if not filenames:
                print("File list is empty")
                return
            
            for filename in filenames:
                print(f"\n===== Starting processing file {filename} =====")
                
                download_request = f"DOWNLOAD {filename}"
                response = self.send_and_receive(download_request, server_address)
                
                if response is None:
                    print(f"Failed to download file {filename}, skipping")
                    continue
                
                parts = response.split()
                if len(parts) < 2:
                    print(f"Received invalid response: {response}")
                    continue
                
                if parts[0] == "OK":
                    if len(parts) < 6 or parts[3] != "SIZE" or parts[5] != "PORT":
                        print(f"Received malformed OK response: {response}")
                        continue
                    
                    file_size = int(parts[4])
                    data_port = int(parts[6])
                    
                    self.download_file(filename, data_port, file_size)
                    
                elif parts[0] == "ERR" and parts[2] == "NOT_FOUND":
                    print(f"File {filename} not found on server")
                else:
                    print(f"Received unknown response: {response}")
                
                print(f"===== Processing file {filename} complete =====")
            
        except Exception as e:
            print(f"Error running client: {e}")
        finally:
            self.client_socket.close()
            print("Client closed")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python3 UDPclient.py <server_host> <server_port> <file_list>")
        sys.exit(1)
    
    server_host = sys.argv[1]
    server_port = int(sys.argv[2])
    file_list = sys.argv[3]
    
    client = UDPClient(server_host, server_port, file_list)
    client.run()