import paramiko
import time
import socket
from pprint import pprint
import re
import yaml
from datetime import datetime
import os
from termcolor import colored, cprint
from sty import fg, bg, ef, rs



def backup_config_ubnt(
        device,
        max_bytes=60000,
        short_pause=1,
        long_pause=5,
        ):
    
    host = device['host']
    username = os.environ.get(device['username'])
    password = os.environ.get(device['password'])

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
            
            
            #ssh.send("cat /tmp/system.cfg\n")            #отправляем команду enable
            ssh.send('\n')
            time.sleep(short_pause)         #делаем короткую паузу
            ssh.recv(max_bytes)         #считываем данные


            
            ssh.send("cat /tmp/system.cfg\n") 
            time.sleep(3) 


            output = ssh.recv(max_bytes).decode("utf-8")          #считываем данные и переводим в utf-8
            time.sleep(0.5)

            #pprint(output)

            regex = (
                     r"cat /tmp/system.cfg\r\n"
                     r"(?P<cfg>(?:.+\n)*)"
                     r"X[MW].+\s+"
                    )

            matches = re.finditer(regex, output)            #выполняем парсинг регуляркой

            for match in matches:
                config = match.group('cfg')


            regex = (
                     r"resolv.host.1.name=(?P<prompt>.+)\r\n"
                    )  
                    

            matches = re.finditer(regex, config)            #выполняем парсинг регуляркой

            for match in matches:
                prompt = match.group('prompt')


            result = {'device': prompt, 'cfg': config}
            
            #print(prompt)
            #print(config)
            #print(result)

            return result

    except:
        print(fg(124) + f'\nОшибка при подключении к устройству {host} ' + fg.rs)
        
        #print(host)
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
    for dev in dev_test:
        device = backup_config_ubnt(dev)
        prompt = device['device']
        config = device['cfg']
        with open(f'{prompt}.cfg', 'w') as f:
            for line in device['cfg']:
                f.write(line)
        cprint(f'\nКонфигурация с устройства {prompt} успешна сохранена\n', 'white', 'on_blue')  
