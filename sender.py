import socket
import sys 
import json
import subprocess
# IP address and port of the receiver
ip_address = '130.225.39.202'  # Replace this with the recipient's IP address
port = 8081  # Replace this with the recipient's port number

pi_private_key = ''
pi_public_key = ''

with open('/etc/wireguard/public-key-matrix-synapse', 'r') as file:
    # Read the first line
    pi_public_key = file.readline()

with open('/etc/wireguard/private-key-matrix-synapse', 'r') as file:
    # Read the first line
    pi_private_key = file.readline()


# Message to be sent
#privateKey = sys.argv[1]
#ip = sys.argv[2]
data = {
    "key": pi_public_key, 
    "domain": 'this is a test domain'
}

message = json.dumps(data)
# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to the server
    client_socket.connect((ip_address, port))

    # Send the message
    client_socket.sendall(message.encode())

    # Receive data from the server (optional)
    response = client_socket.recv(1024)
    print('Received:', response.decode())
    received_msg = json.loads(response.decode())



    #FOR ADDING RETURNED IP TO CONFIG AND UPDATE CONFIG
    
    # File path
    
    file_path = '/etc/wireguard/wgmatrixsynapse.conf'
    

    # Line number you want to replace
    line_number = 2

    # New text to replace the line with
    new_text = 'Address = ' + response.decode() + '/24'

    # Read the content of the file into memory



    with open(file_path, 'w') as file:
        lines_to_add = ['[Interface]\n',
                'Address = ' + received_msg['assigned_ip'] + '/24' + '\n',
                'PrivateKey = ' + pi_private_key, 
                'DNS = 8.8.8.8\n',
                '\n',
                '[Peer]\n',
                'PublicKey = ' + received_msg['proxy_public_key'],
                'Endpoint = ' + ip_address + ':51820\n',
                'AllowedIPs = 10.0.0.0/24, 192.168.1.0/24\n',
                'PersistentKeepalive = 25']
        file.writelines(lines_to_add)







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


finally:
    # Close the socket
    client_socket.close()
