import socket
import sys 
import json
import subprocess


class NetworkModule: 
    def __init__(self): 
        # Create a TCP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def send(self, pi_public_key, ip_address, port): 
        data_to_send = {
            "key": pi_public_key,
            "domain": 'domain'
        }
        message = json.dumps(data_to_send)

        # Connect to the server
        self.client_socket.connect((ip_address, port))
        # Send the message
        self.client_socket.sendall(message.encode())

    def receive(self): 
        # Receive data from the server (optional)
        response = self.client_socket.recv(1024)
        print('Received:', response.decode())
        received_msg = json.loads(response.decode())
    
    def close(self): 
        # Close the socket
        self.client_socket.close()

class WireguardModule: 

    def __init__(self): 
        with open('/etc/wireguard/public-key-matrix-synapse', 'r') as file:
            # Read the first line
            self.pi_public_key = file.readline()

        with open('/etc/wireguard/private-key-matrix-synapse', 'r') as file:
            # Read the first line
            self.pi_private_key = file.readline()

        self. file_path = '/etc/wireguard/wgmatrixsynapse.conf'
    
    def updateConfig(self, internal_ip, proxy_public_key, proxy_ip):        
        with open(self.file_path, 'w') as file:
            lines_to_add = ['[Interface]\n',
                    'Address = ' + ip + '/24' + '\n',
                    'PrivateKey = ' + self.pi_private_key + '\n', 
                    'DNS = 8.8.8.8\n',
                    '\n',
                    '[Peer]\n',
                    'PublicKey = ' + proxy_public_key,
                    'Endpoint = ' + proxy_ip + ':51820\n',
                    'AllowedIPs = 10.0.0.0/24\n',
                    'PersistentKeepalive = 25']
            file.writelines(lines_to_add)
    
    def reloadService(self): 
        # Run a shell command which updates wireguard interface without interupting established connections 
        start_wireguard_command = "sudo systemctl start wg-quick@wgmatrixsynapse"
        enable_wireguard_command = "sudo systemctl enable wg-quick@wgmatrixsynapse"
        subprocess.run(start_wireguard_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        subprocess.run(enable_wireguard_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


        #result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Print the output of the command
        #print("Output:", result.stdout)

        # Print any errors that occurred during the command execution
        #print("Errors:", result.stderr)

        # Print the return code of the command
        #print("Return Code:", result.returncode)











if __name__ == "__main__":
    #Create objects
    connection = NetworkModule()
    wireguard = WireguardModule()

    #Listen for connection and receive data
    connection.send('testkey', '130.225.39.202', 8081)
    connection.receive()

    #Update wireguard with client info
    wireguard.updateConfig(connection.received_msg['assigned_ip'], connection.received_msg['proxy_public_key'], '130.225.39.202')
    wireguard.reloadService()

    #send back public key of proxy server and close connection
    connection.close()


































