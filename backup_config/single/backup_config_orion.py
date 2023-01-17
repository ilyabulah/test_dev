import paramiko
import time
import socket
from pprint import pprint
import re
import yaml
from datetime import datetime
import os
from termcolor import colored, cprint
import shutil

def backup_config_orion(
        device,
        max_bytes=60000,
        short_pause=1,
        long_pause=5,
        ):
    host = device['host']
    #username = device['username']
    username = os.environ.get(device['username'])
    print(username)
    #password = device['password']
    password = os.environ.get(device['password'])
    #secret = device['secret']
    secret = os.environ.get(device['secret'])

    cl = paramiko.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(
        hostname=host,
        username=username,
        password=password,
        look_for_keys=False,
        allow_agent=False,
    )



    with cl.invoke_shell() as ssh:

        #print(f'\nПодключаюсь к {host}...') 
        
        
        ssh.send("enable\n")            #отправляем команду enable
        time.sleep(short_pause)         #делаем короткую паузу
        ssh.recv(max_bytes)         #считываем данные
        time.sleep(short_pause)

        
        ssh.send("\n")
        time.sleep(short_pause)         #делаем короткую паузу
        promt = ssh.recv(max_bytes).decode("utf-8")          #считываем данные и переводим в utf-8
        promt = promt.replace('#','').strip()

       
        #pprint(promt)

        ssh.send(f"upload running-config tftp 172.23.16.55 {promt}.txt\n")
        time.sleep(5)

        return promt

   





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
        hostname = backup_config_orion(dev)
        shutil.copy(f"/var/tftp/{hostname}.txt", f"/mnt/backup_config/test/{today}/{hostname}.txt")
        os.remove(f"/var/tftp/{hostname}.txt")
        cprint(f'\nКонфигурация с устройства {hostname} успешна сохранена\n', 'white', 'on_blue')
