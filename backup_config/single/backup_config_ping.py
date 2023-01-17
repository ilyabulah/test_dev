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
import subprocess
from concurrent.futures import ThreadPoolExecutor

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


def ping_ip(ip):
    result = subprocess.run(["ping", "-c", "3", "-n", ip], stdout=subprocess.DEVNULL)
    ip_is_reachable = result.returncode == 0
    return ip_is_reachable


def ping_ip_addresses(ip_list, limit=3):
    reachable = []
    unreachable = []
    with ThreadPoolExecutor(max_workers=limit) as executor:
        results = executor.map(ping_ip, ip_list)
    for ip, status in zip(ip_list, results):
        if status:
            reachable.append(ip)
        else:
            unreachable.append(ip)
    return unreachable


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

    ip_list = []    
    for device in region.values():
        for dev in device:
            ip_list.append(dev['host'])

    print(ping_ip_addresses(ip_list))
