import paramiko
import time
import socket
from pprint import pprint
import re
from tabulate import tabulate
from find_mac_address import send_show_mac_address
import yaml
from correct_mac_from_bdcom import input_correct_mac_address_for_bdcom
from datetime import datetime
from termcolor import colored, cprint


def send_show_optical_inform(
        host,
        username,
        password,
        #secret,
        epon_intf,
        #command,
        max_bytes=60000,
        short_pause=1,
        long_pause=5,
        ):
    
    #start_time = datetime.now()

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

        cprint(f'''
Ура!!! Я нашел введенный тобой MAC адрес.
Подключаюсь к {host}...
               ''', 'green')
                
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


        command = f"show ep\tinterface {epon_intf} onu ctc optical-transceiver-diagnosis"
        ssh.send(f'{command}\n')            #отправляем команду на устройство
        time.sleep(short_pause)
        ssh.settimeout(5)

        command = f"show ep\toptical-transceiver-diagnosis"
        ssh.send(f"{command}\n")            #отправляем команду на устройство
        time.sleep(short_pause)
        ssh.settimeout(5)

        command = f"show ep\toptical-transceiver-diagnosis interface {epon_intf}"
        ssh.send(f"{command}\n")            #отправляем команду на устройство
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

        #print(output)

        

        regex = (
                 r" transmitted power\(DBm\): (?P<onu_tx_power>.+)\r\n"
                 r" received power\(DBm\): (?P<onu_rx_power>.+)\r\n"
                 r"(?:.+\n)*"
                 r'{0}\s+\S+\s+\S+\s+\S+\s+(?P<OLT_tx_power>\S+)\s+\r\n'
                 r"(?:.+\n)*"
                 r'{1}\s+(?P<OLT_rx_power>\S+)\s+\r\n'.format(epon_intf[0:7],epon_intf)

                 )

        matches = re.finditer(regex, output)            #выполняем парсинг регуляркой
        result = []
        intf_list = []

        for match in matches:
            onu_rx_power = match.group('onu_rx_power')
            onu_tx_power = match.group('onu_tx_power')
            OLT_tx_power = match.group('OLT_tx_power')
            OLT_rx_power = match.group('OLT_rx_power')
        
        '''
        print('#' * 100)
        print(onu_rx_power)
        print(onu_tx_power)
        print(OLT_tx_power)
        print(OLT_rx_power)
        '''
        
        result_list = [{'Device': 'ONU',
                        'Rx': onu_rx_power,
                        'Tx': onu_tx_power},
                       {'Device': 'OLT',
                        'Rx': OLT_rx_power,
                        'Tx': OLT_tx_power}]


        print('\n')        
        cprint(f'Уровни сигнала в DBm полученные с оборудования', 'white', 'on_blue')
        print(f'{promt} c ip адресом {host} на интерфейсе {epon_intf}')
        print(tabulate(result_list, headers='keys', tablefmt="grid", numalign='center', stralign='center'))         #выводим информацию в табличном виде
        print('\n')
        #time_script = datetime.now() - start_time
        #print(f'Время выполнения скрипта: {time_script}')
        
        #print('\nКонец')
        







if __name__ == "__main__":
   
    mac_addr = input_correct_mac_address_for_bdcom()
    
    start_time = datetime.now()
   

    option = input(f'''\nВыберите на каком оборудовании вы хотите искать mac адрес и получить данные по отическому сигналу\n
    1 - Мухоршибирь\n
    2 - Саган-нур\n
    ''')
    
    with open("mukhorshibir.yaml") as f:
        dev_muh = yaml.safe_load(f)
    
   
    with open("sagan-nur.yaml") as f:
        dev_sag = yaml.safe_load(f)

    if option == '1':
        ip_list = []
        for dev in dev_muh:
            output = ''
            output = send_show_mac_address(dev['host'], dev['username'], dev['password'], mac_addr)

            if output:
                send_show_optical_inform(output['result_dict']['host'], dev['username'], dev['password'], output['result_dict']['epon_intf'])
                break
           
            else:
                ip_list.append(dev['host'])
        
        if ip_list:    
            cprint(f'\nНа устройствах с ip адресами {ip_list} нет такого MAC адреса\n', 'red')
        
        time_script = datetime.now() - start_time
        cprint(f'Время выполнения скрипта: {str(time_script)[0:7]} сек.\n', 'white', 'on_magenta')


    if option == '2':
        ip_list = []
        for dev in dev_sag:
            output = ''
            output = send_show_mac_address(dev['host'], dev['username'], dev['password'], mac_addr)

            if output:
                send_show_optical_inform(output['result_dict']['host'], dev['username'], dev['password'], output['result_dict']['epon_intf'])
                break
            else:
                ip_list.append(dev['host'])
        
        if ip_list:   
            cprint(f'\nНа устройствах с ip адресами {ip_list} нет такого MAC адреса\n', 'red')
        
        time_script = datetime.now() - start_time
        cprint(f'Время выполнения скрипта: {str(time_script)[0:7]}сек.\n', 'white', 'on_magenta')
            


