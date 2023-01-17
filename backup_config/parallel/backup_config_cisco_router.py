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


def backup_config_cisco_router(device):
    username = os.environ.get(device['username'])
    password = os.environ.get(device['password'])
    if device['secret']:
        secret = os.environ.get(device['secret'])
        device['secret'] = secret

    device['username'] = username
    device['password'] = password




    try:
        
        with ConnectHandler(**device) as ssh:
            ssh.enable()
            prompt = ssh.find_prompt()
            prompt = prompt.replace('#','')
            #print(prompt)
            ssh.send_command('terminal length 0')
            output = ssh.send_command('show running-config', strip_command=True, strip_prompt=True)
            time.sleep(3)
            #print(output)
            #ssh.send_command('/n')

            #ssh.send_command('/n')
            
            result = {'device': prompt, 'cfg': output}
            #print(result)
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
        device = backup_config_cisco_router(dev)
        prompt = device['device']
        config = device['cfg']
        with open(f'{prompt}.txt', 'w') as f:
            for line in config:
                f.write(line)
        cprint(f'\nКонфигурация с устройства {prompt} успешна сохранена\n', 'white', 'on_blue')
