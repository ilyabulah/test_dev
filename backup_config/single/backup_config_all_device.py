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
from backup_config_bdcom import backup_config_bdcom
from backup_config_eltex_new import backup_config_eltex_new
from backup_config_eltex_old import backup_config_eltex_old
from backup_config_orion import backup_config_orion
from backup_config_snr import backup_config_snr
from backup_config_ubnt import backup_config_ubnt
from sty import fg, bg, ef, rs

def write_to_txt_file(device_dict):
    
    promt = device_dict['device']
    config = device_dict['cfg']

    with open(f'{promt}.txt', 'w') as f:
        for line in config:
            f.write(line)
        print(fg.da_green + f'\nКонфигурация с устройства {promt} успешна сохранена' + fg.rs)

def write_to_cfg_file(device_dict):

    promt = device_dict['device']
    config = device_dict['cfg']

    with open(f'{promt}.cfg', 'w') as f:
        for line in config:
            f.write(line)
        print(fg.da_green + f'\nКонфигурация с устройства {promt} успешна сохранена' + fg.rs)



def move_config_to_nas(hostname, directory):

    shutil.copy(f"/var/tftp/{hostname}.txt", f"/mnt/backup_config/{directory}/{today}/{hostname}.txt")
    os.remove(f"/var/tftp/{hostname}.txt")
    print(fg.da_green + f'\nКонфигурация с устройства {hostname} успешна сохранена' + fg.rs)




if __name__ == "__main__":
   
    start_time = datetime.now() 
    today = datetime.now().date()
    today = str(today)
   
    with open("mukhorshibir.yaml") as f:
        dev_muh = yaml.safe_load(f)
    
    with open("sagan-nur.yaml") as f:
        dev_sag = yaml.safe_load(f)
    
    region = {'muh': dev_muh, 'sag': dev_sag}
    name = {'muh': 'п.Мухоршибирь', 'sag': 'п.Саган-Нур'}

    for directory, devices in region.items():
        os.chdir(f"/mnt/backup_config/{directory}")

        if not os.path.isdir(today):
            os.mkdir(today)

        os.chdir(f"/mnt/backup_config/{directory}/{today}")

        location = name.setdefault(directory)
        print(fg(201) + f'\n\nСобираем информацию с оборудования в {location}\n' + fg.rs)

        for dev in devices:
        
            if dev['device_type'] == 'eltex_new':
                try:
                    print(f'\nПодключаюсь к {dev["host"]}...')
                    hostname = backup_config_eltex_new(dev)
                except (ValueError, OSError):
                    print(fg.da_red + f"Что-то пошло не так..." + fg.rs)
                    continue
                else:
                    move_config_to_nas(hostname, directory)
        
            elif dev['device_type'] == 'switch_orion':
                try:
                    print(f'\nПодключаюсь к {dev["host"]}...')
                    hostname = backup_config_orion(dev)
                except (ValueError, OSError):
                    print(fg.da_red + f"Что-то пошло не так..." + fg.rs)
                    continue
                else:
                    move_config_to_nas(hostname, directory)

            elif dev['device_type'] == 'eltex_old':
                try:
                    print(f'\nПодключаюсь к {dev["host"]}...')
                    device_dict = backup_config_eltex_old(dev)
                except (ValueError, OSError):
                    print(fg.da_red + f"Что-то пошло не так..." + fg.rs)
                    continue
                else:
                    write_to_txt_file(device_dict)

            elif dev['device_type'] == 'bdcom':
                try:
                    print(f'\nПодключаюсь к {dev["host"]}...')
                    device_dict = backup_config_bdcom(dev)
                except (ValueError, OSError):
                    print(fg.da_red + f"Что-то пошло не так..." + fg.rs)
                    continue
                else:
                    write_to_txt_file(device_dict)

            elif dev['device_type'] == 'switch_snr':
                try:
                    print(f'\nПодключаюсь к {dev["host"]}...')
                    device_dict = backup_config_snr(dev)
                except (ValueError, OSError):
                    print(fg.da_red + f"Что-то пошло не так..." + fg.rs)
                    continue
                else:
                    write_to_txt_file(device_dict)

            elif dev['device_type'] == 'ubnt':
                try:
                    print(f'\nПодключаюсь к {dev["host"]}...')
                    device_dict = backup_config_ubnt(dev)
                except (ValueError, OSError):
                    print(fg.da_red + f"Что-то пошло не так..." + fg.rs)
                    continue
                else:
                    write_to_cfg_file(device_dict)

    
    time_script = datetime.now() - start_time
    print('\n')
    print(fg(208) + f'Время выполнения скрипта: {str(time_script)[0:7]}сек.' + fg.rs)
    print('\n')
