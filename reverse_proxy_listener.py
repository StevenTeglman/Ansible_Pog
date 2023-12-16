import socket
import json
import subprocess
import re
class NetworkModule: 
    def __init__(self):

        #Proxy Server
        self.ip = '0.0.0.0' # Listen on all available network interfaces
        self.port = 8081

        #Client that is establishing connection
        self.ip_template = '10.0.0.'
        self.current_ip = 1
        self.peer_ip = f"{self.ip_template}{self.current_ip}"

        # Create a TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the IP address and port
        self.server_socket.bind((self.ip, self.port))

        #Client info
        self.client_socket = None 
        self.client_address = None
        self.received_msg = None
        
    def listen(self): 
        print(f"Listening for TCP connections on {self.ip}:{self.port}...")
        # Listen for incoming connections (max 1 pending connection)
        self.server_socket.listen(1)

    def accept(self):
        # Accept incoming connection
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"Accepted connection from {self.client_address}")

    def receive(self):
        # Receive data from the client
        data = self.client_socket.recv(1024)  # Receive up to 1024 bytes of data
        self.received_msg = json.loads(data.decode())
        print(f"Received data: {data.decode()}")
        
    def send(self, proxy_public_key): 
        data_to_send = {
            "assigned_ip": self.peer_ip,
            "proxy_public_key": proxy_public_key
        }

        message = json.dumps(data_to_send)
        self.client_socket.sendall(message.encode())

    def sendError(self, message): 
        data_to_send = {
            "error": message,
        }

        message = json.dumps(data_to_send)
        self.client_socket.sendall(message.encode())

    def close(self): 
        self.current_ip += 1
        self.peer_ip = f"{self.ip_template}{self.current_ip}"

        # Close the sockets
        self.client_socket.close()

class NginxModule: 

    def updateConfig(self, peer_ip):
        nginx_config = f"""
server {{
    listen 130.225.39.202:80;
    server_name 130.225.39.202;

    location / {{
        proxy_pass http://{peer_ip}:8008;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
        """

        with open('/etc/nginx/sites-available/matrix-synapse-proxy.conf', 'a') as file:
            file.write(nginx_config)

    def reloadService(self):
        # Run a shell command which updates wireguard interface without interupting established connections 
        command = "sudo systemctl reload nginx"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Print the output of the command
        print("Output:", result.stdout)
        # Print any errors that occurred during the command execution
        print("Errors:", result.stderr)
        # Print the return code of the command
        print("Return Code:", result.returncode)

    def isDomainTaken(self, search_string):
        try:
            with open('/etc/nginx/sites-available/matrix-synapse-proxy.conf', 'r') as file:
                content = file.read()
                match = re.search(search_string, content)
                if match:
                    print(f"Found '{search_string}' in the file.")
                    print("Match:", match.group())
                else:
                    print(f"'{search_string}' not found in the file.")
        except FileNotFoundError:
            print("File /etc/nginx/sites-available/matrix-synapse-proxy.conf not found.")

class WireguardModule: 
    def __init__(self):

        with open('/etc/wireguard/public-key-reverse-proxy', 'r') as file:
            # Read the first line
            self.proxy_public_key = file.readline()

    def updateConfig(self, peer_public_key, peer_ip): 
        wireguard_config = f"""
[Peer]
PublicKey = {peer_public_key}
AllowedIPs = {peer_ip}/32
        """

        with open('/etc/wireguard/wgreverseproxy.conf', 'a') as file:
            file.write(wireguard_config)

    def reloadService(self):
        # Run a shell command which updates wireguard interface without interupting established connections 
        command = "sudo systemctl reload wg-quick@wgreverseproxy"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Print the output of the command
        print("Output:", result.stdout)
        # Print any errors that occurred during the command execution
        print("Errors:", result.stderr)
        # Print the return code of the command
        print("Return Code:", result.returncode)

if __name__ == "__main__":
    #Create objects
    connection = NetworkModule()
    proxy = NginxModule()
    wireguard = WireguardModule()

    while(True):
        #Listen for connection and receive data
        connection.listen()
        connection.accept()
        connection.receive()

        if proxy.isDomainTaken(connection.received_msg['domain']):
            connection.sendError("Domain is already taken")
            connection.close()
        else: 
            '''
            #Update wireguard with client info
            wireguard.updateConfig(connection.received_msg['key'], connection.peer_ip)
            wireguard.reloadService()

            #Update nginx with client info
            proxy.updateConfig(connection.peer_ip)
            proxy.reloadService()

            #send back public key of proxy server and close connection
            connection.send(wireguard.proxy_public_key)
            connection.close()
            '''

