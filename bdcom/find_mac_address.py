import paramiko
import time
import socket
from pprint import pprint
import re
from tabulate import tabulate
import yaml
from correct_mac_from_bdcom import input_correct_mac_address_for_bdcom
#from termcolor import colored, cprint


def send_show_mac_address(
    host,
    username,
    password,
    #secret,
    mac_addr,
    #command,
    max_bytes=60000,
    short_pause=1,
    long_pause=5,
    ):

    '''
    Функция подключается к оборудованию BDCOM, отправляет команду show mac address table 
    с mac адресом, который ввел пользователь. Затем парсится вывод и выводится полученные данные 
    в табличном виде
    '''


    cl = paramiko.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(
        hostname = host,
        username = username,
        password = password,
        look_for_keys=False,
        allow_agent=False,
    )

    with cl.invoke_shell() as ssh:

        
        ssh.send("enable\n")            #отправляем команду enable
        #ssh.send(f"{secret}\n")
        time.sleep(short_pause)         #делаем короткую паузу
        ssh.recv(max_bytes)         #считываем данные
        ssh.send("\n")
        time.sleep(short_pause)         #делаем короткую паузу
        promt = ssh.recv(max_bytes).decode("utf-8")          #считываем данные и переводим в utf-8
        promt = promt.replace('#','').strip()
        ssh.send("terminal length 0\n")         #отключаем пэйджинг
        time.sleep(short_pause)
        ssh.recv(max_bytes)         #считываем данные


        command = f"show mac address-table {mac_addr}"
        ssh.send(f'{command}\n')            #отправляем команду на устройство
        ssh.settimeout(5)
        output = ""


        while True:
            try:
                part = ssh.recv(max_bytes).decode("utf-8")          #считываем данные и переводим в utf-8
                output += part
                time.sleep(0.5)
            except socket.timeout:
                break
        
            
        regex = (
                  r"(?P<Vlan>\d+)\s+(?P<MAC>\S+)\s+\S+\s+(?P<Interface>\S+)\s+\n"
                 )

        matches = re.finditer(regex, output)            #выполняем парсинг регуляркой
        result_list = []
        intf_list = []
        result_dict = {}

        for match in matches:
            output = match.groupdict()
            result_list.append(output)           #добавляем пропарсенные словари в список
            intf = match.group('Interface')
            intf_list.append(intf)
        
        for interface in intf_list:
            if 'epon' in interface:
                intf = interface


        if result_list:    
            
            result = {
                      'result_dict': {'host':host, 'epon_intf':intf},
                      'result_list': result_list
                      }

            
            return result
        
        #else:
            #print('\n')
            #print(f'На устройстве {promt} с ip адресом {host} нет такого MAC адреса!')
            #print('\n')





if __name__ == "__main__":

    mac_addr = input_correct_mac_address_for_bdcom()            #выполняем функцию для ввода mac адреса пользователем

    with open("mukhorshibir.yaml") as f:
        devices = yaml.safe_load(f)
    
    for dev in devices:
        output = send_show_mac_address(dev['host'], dev['username'], dev['password'], mac_addr)
        
        if output:
            print(tabulate(output['result_list'], headers='keys', tablefmt="grid", numalign='center', stralign='center'))         #выводим информацию в табличном виде
            break
