import paramiko
import time
import socket
from pprint import pprint
import re
import yaml
from datetime import datetime
import os
from termcolor import colored, cprint
from concurrent.futures import ThreadPoolExecutor
from sty import fg, bg, ef, rs


def backup_config_snr(
        device,
        max_bytes=60000,
        short_pause=1,
        long_pause=5,
        ):
    
    host = device['host']
    username = os.environ.get(device['username'])
    password = os.environ.get(device['password'])
    secret = os.environ.get(device['secret'])

    try:

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


            
            ssh.send("\n")
            time.sleep(short_pause)         #делаем короткую паузу
            promt = ssh.recv(max_bytes).decode("utf-8")          #считываем данные и переводим в utf-8
            promt = promt.replace('#','').strip()

           
            #pprint(promt)

            ssh.send("terminal length 0\n")         #отключаем пэйджинг
            time.sleep(short_pause)
            ssh.recv(max_bytes)         #считываем данные



            command = f"show run\t"
            ssh.send(f'{command}\n')            #отправляем команду на устройство
            time.sleep(short_pause)
            ssh.settimeout(5)

            output = ""
            

            while True:
                try:
                    part = ssh.recv(max_bytes).decode("utf-8")          #считываем данные и переводим в utf-8
                    output += part
                    time.sleep(0.5)
                except socket.timeout:
                    break
            
            #pprint(output)
            result = {'device': promt, 'cfg': output}
            
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
    

    print('\nСобираем информацию с оборудования в Тестовом режиме\n')

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(backup_config_snr, dev_test)
    for output in results:
        #print(ip)
        print(output['cfg'])
    

'''
    for dev in dev_test:
        device = backup_config_snr(dev)
        promt = device['device']
        config = device['cfg']
        with open(f'{promt}.txt', 'w') as f:
            for line in config:
                f.write(line)
        cprint(f'\nКонфигурация с устройства {promt} успешна сохранена\n', 'white', 'on_blue')  
'''
