import time
import socket
from pprint import pprint
import yaml
from datetime import datetime
import os
from termcolor import colored, cprint
import shutil
from sty import fg, bg, ef, rs
from netmiko import ConnectHandler


def backup_config_zte(device):
    username = os.environ.get(device['username'])
    password = os.environ.get(device['password'])
    #secret = os.environ.get(device['secret'])
    device['username'] = username
    device['password'] = password
    #device['secret'] = secret




    try:
        
        with ConnectHandler(**device) as ssh:
            ssh.enable()
            prompt = ssh.find_prompt()
            prompt = prompt.replace('#','')
            ssh.send_command(f'copy tftp root: DATA0/startrun.dat //172.23.16.55/{prompt}.dat')
            time.sleep(2)

            result = {'hostname': prompt}
            
            return result
    
    except:

        print(fg(124) + f'\nОшибка при подключении к устройству {device["host"]} ' + fg.rs)

        return str(device["host"])



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

    print('\nСобираем информацию с оборудования в Тестовом режиме\n')
    for dev in dev_test:
        result = backup_config_zte(dev)
        hostname = result['hostname']
        shutil.copy(f"/var/tftp/{hostname}.dat", f"/mnt/backup_config/test/{today}/{hostname}.dat")
        os.remove(f"/var/tftp/{hostname}.dat")
        cprint(f'\nКонфигурация с устройства {hostname} успешна сохранена\n', 'white', 'on_blue')
