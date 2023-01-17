import time
import socket
from pprint import pprint
import re
import yaml
from datetime import datetime
import os
import shutil
from termcolor import colored, cprint
import pexpect
from sty import fg, bg, ef, rs




def backup_config_eltex_new(device, promt='#'):
    host = device['host']
    username = os.environ.get(device['username'])
    password = os.environ.get(device['password'])
    secret = os.environ.get(device['secret'])
    
    try:

        with pexpect.spawn(f"ssh -c aes256-cbc -oKexAlgorithms=+diffie-hellman-group1-sha1 {username}@{host}", timeout=10, encoding="utf-8") as ssh:
            #print(f'\nПодключаюсь к {host}...')
        
            ssh.expect("Password:")
            ssh.sendline(password)
            ssh.expect("User Name:")
            ssh.sendline(username)
            ssh.expect(promt)
            
           
            ssh.sendline('\n')
            ssh.expect(promt)
            hostname = ssh.before
             
            if '\x1b[K' in hostname:
                hostname = hostname.replace('\x1b[K', '').strip()
            
            #pprint(hostname)
            ssh.sendline(f'copy running-config tftp://172.23.16.55/{hostname}.txt')
            time.sleep(8)
            output = ''
            
            while True:

                match = ssh.expect([promt, pexpect.TIMEOUT])
                output = ssh.before
            
                if match == 0:
                    break
                
                else:
                    print("Ошибка: timeout")
                    break

            
            result = {'hostname': hostname}
            
            return result



    except:

        print(fg(124) + f'\nОшибка при подключении к устройству {host} ' + fg.rs)

        return str(host)




if __name__ == "__main__":
   
   
    today = datetime.now().date()
    today = str(today)
   
    with open("test.yaml") as f:
        dev_test = yaml.safe_load(f)
    
    # изменение текущего каталога на папку с бэкапами
    os.chdir("/mnt/backup_config/test")

    if not os.path.isdir(today):
        os.mkdir(today)

    os.chdir(f"/mnt/backup_config/test/{today}")

    print('\nСобираем информацию с тестового оборудования\n')
    for dev in dev_test:
        result = backup_config_eltex_new(dev)
        hostname = result['hostname']
        shutil.copy(f"/var/tftp/{hostname}.txt", f"/mnt/backup_config/test/{today}/{hostname}.txt")
        os.remove(f"/var/tftp/{hostname}.txt")
        cprint(f'\nКонфигурация с устройства {hostname} успешна сохранена\n', 'white', 'on_blue')

