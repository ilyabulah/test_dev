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


def ping_ip_addresses(ip_list, limit=21):
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
 
    #with open("mukhorshibir.yaml") as f:
    #    dev_muh = yaml.safe_load(f)
    #
    #with open("sagan-nur.yaml") as f:
    #    dev_sag = yaml.safe_load(f)
    #
    #with open("gusinoozersk.yaml") as f:
    #    dev_gus = yaml.safe_load(f)
    
    #region = {'muh': dev_muh, 'sag': dev_sag, 'gus': dev_gus}
    #region = {'muh': dev_muh}
    #name = {'muh': 'п.Мухоршибирь', 'sag': 'п.Саган-Нур', 'gus': 'г.Гусиноозерск'}
    
    with open("test.yaml") as f:
        dev_test = yaml.safe_load(f)

    region = {'test': dev_test}

    name = {'test': 'Тестовое'}

    ip_list = []    
    for device in region.values():
        for dev in device:
            ip_list.append(dev['host'])

    print('\n')
    print(fg(208) + f'Выполняю ICMP запросы на оборудование' + fg.rs)
    print('\n')
    unreachable_ip = ping_ip_addresses(ip_list)
    
    print(unreachable_ip)

    for directory, devices in region.items():
        os.chdir(f"/mnt/backup_config/{directory}")

        if not os.path.isdir(today):
            os.mkdir(today)

        os.chdir(f"/mnt/backup_config/{directory}/{today}")

        location = name.setdefault(directory)
        print(fg(201) + f'\n\nСобираем информацию с оборудования в {location}\n' + fg.rs)

        list_files = []

        for dev in devices:

            if dev['host'] not in unreachable_ip:

                list_dict = [] 

                if dev['device_type'] == 'eltex_new':
                    list_dict.append(dev)
                    list_files.append('eltex_new')
                    with open('eltex_new.yaml', 'a') as f:
                        yaml.dump(list_dict, f)

                elif dev['device_type'] == 'switch_orion':
                    list_dict.append(dev)
                    list_files.append('switch_orion')
                    with open('switch_orion.yaml', 'a') as f:
                        yaml.dump(list_dict, f)

                elif dev['device_type'] == 'eltex_old':
                    list_dict.append(dev)
                    list_files.append('eltex_old')
                    with open('eltex_old.yaml', 'a') as f:
                        yaml.dump(list_dict, f)

                elif dev['device_type'] == 'bdcom':
                    list_dict.append(dev)
                    list_files.append('bdcom')
                    with open('bdcom.yaml', 'a') as f:
                        yaml.dump(list_dict, f)

                elif dev['device_type'] == 'switch_snr':
                    list_dict.append(dev)
                    list_files.append('switch_snr')
                    with open('switch_snr.yaml', 'a') as f:
                        yaml.dump(list_dict, f)

                elif dev['device_type'] == 'ubnt':
                    list_dict.append(dev)
                    list_files.append('ubnt')
                    with open('ubnt.yaml', 'a') as f:
                        yaml.dump(list_dict, f)
        
        #print(list_files)
        

        ip_con_error = []

        if 'eltex_new' in list_files:
            with open("eltex_new.yaml") as f:
                dev_eltex_new = yaml.safe_load(f)
            os.remove("eltex_new.yaml")

            with ThreadPoolExecutor(max_workers=21) as executor:
                results = executor.map(backup_config_eltex_new, dev_eltex_new)
                for output in results:
                    if type(output) is dict:
                        move_config_to_nas(output['hostname'], directory)
                    else:
                        ip_con_error.append(output)


        if 'switch_orion' in list_files:
            with open("switch_orion.yaml") as f:
                dev_switch_orion = yaml.safe_load(f)
            os.remove("switch_orion.yaml")

            with ThreadPoolExecutor(max_workers=21) as executor:
                results = executor.map(backup_config_orion, dev_switch_orion)
                for output in results:
                    if type(output) is dict:
                        move_config_to_nas(output['hostname'], directory)
                    else:
                        ip_con_error.append(output)


        if 'eltex_old' in list_files:
            with open("eltex_old.yaml") as f:
                dev_eltex_old = yaml.safe_load(f)
            os.remove("eltex_old.yaml")

            with ThreadPoolExecutor(max_workers=21) as executor:
                results = executor.map(backup_config_eltex_old, dev_eltex_old)
                for output in results:
                    if type(output) is dict:
                        write_to_txt_file(output)
                    else:
                        ip_con_error.append(output)


        if 'bdcom' in list_files:
            with open("bdcom.yaml") as f:
                dev_bdcom = yaml.safe_load(f)
            os.remove("bdcom.yaml")

            with ThreadPoolExecutor(max_workers=21) as executor:
                results = executor.map(backup_config_bdcom, dev_bdcom)
                for output in results:
                    if type(output) is dict:
                        write_to_txt_file(output)
                    else:
                        ip_con_error.append(output)


        if 'switch_snr' in list_files:
            with open("switch_snr.yaml") as f:
                dev_switch_snr = yaml.safe_load(f)
            os.remove("switch_snr.yaml")
            
            with ThreadPoolExecutor(max_workers=21) as executor:
                results = executor.map(backup_config_snr, dev_switch_snr)
                for output in results:
                    if type(output) is dict:
                         write_to_txt_file(output)
                    else:
                        ip_con_error.append(output)


        if 'ubnt' in list_files:
            with open("ubnt.yaml") as f:
                dev_ubnt = yaml.safe_load(f)
            os.remove("ubnt.yaml")

            with ThreadPoolExecutor(max_workers=21) as executor:
                results = executor.map(backup_config_ubnt, dev_ubnt)
                for output in results:
                    if type(output) is dict:
                        write_to_cfg_file(output)
                    else:
                        ip_con_error.append(output)

    print(ip_con_error)
    
    not_backup_ip = ip_con_error + unreachable_ip

    if not_backup_ip:
        print(fg(124) + f'\nСписок ip адресов оборудования, с которых резервная копия конфигурации не была скопирована {not_backup_ip}\n' + fg.rs)
        os.chdir(f"/mnt/backup_config")
        with open(f'Errors_backup_{today}.txt', 'w') as f:
            for ip_addr in not_backup_ip:
                f.write(ip_addr + '\n')
                
    time_script = datetime.now() - start_time
    print('\n')
    print(fg(208) + f'Время выполнения скрипта: {str(time_script)[0:7]}сек.' + fg.rs)
    print('\n')


