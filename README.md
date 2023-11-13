# Matrix Ansible Setup

## Install WSL if on windows:
1. https://learn.microsoft.com/en-us/windows/wsl/install

2. https://pypa.github.io/pipx/installation/

apt install python3.10-venv
apt-get install sshpass

3. Make sure to add the pi's SSH key to your WSL instance with
```
ssh-keyscan -H <Pi's Hostname> >> ~/.ssh/known_hosts
```
in my case:
```
ssh-keyscan -H pi.local >> ~/.ssh/known_hosts
```
4.1 Navigate to etc/ansible (might have to create it)
4.2 sudo nano hosts
4.3 create your group with square brackets
	insert your pi's host name or 
	
	```  
	[raspberrypi]
	<Pi's hostname> ansible_ssh_pass=pi ansible_user=pi




