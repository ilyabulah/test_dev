def input_correct_mac_address_for_bdcom():
    '''
    Функция просит у пользователя ввести mac адрес в любом формате
    затем она преобразует mac адрес в формат xxxx.xxxx.xxxx
    '''

    print('\n')
    mac = input('Введите mac адрес: ')
    mac_correct = False
    while not mac_correct:          #выполняет действия в цикле пока значение mac_correct не будет True
        if not mac[4] == '.':
            
            if mac[4] == ':':
                mac = mac.replace(":", ".")         #делает замену символов : на символ .
                mac_correct = True

            elif mac[4] == '-':
                mac = mac.replace("-", ".")
                mac_correct = True

            elif mac[2] == ':':
                part1,part2,part3,part4,part5,part6 = mac.split(':')            #делит введенный mac адрес пользователя по :
                mac = f'{part1}{part2}.{part3}{part4}.{part5}{part6}'           #соединяет части используя разделитель . в нужный формат
                mac_correct = True

            else:
                print('Неправильный mac-адрес')
                mac = input('Введите mac адрес ещё раз: ')
                continue

                
        else:
            mac_correct = True
            continue


    return mac
