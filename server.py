import socket
import datetime
import random
import hashlib
f = open('log.txt', 'w')


def logger(message: str) -> None:
    f.write(message + ' | ' + str(datetime.datetime.now()) + '\n')
    print(message)


def sender(sock: socket.socket, message: str) -> None:
    sock.send(bytearray(f'{len(message)}~{message}'.encode()))


def reciever(sock: socket.socket) -> str:
    message = sock.recv(1024).decode()
    print(f"Получено сообщение длины: {message[:message.index('~')]}")
    return message[message.index('~') + 1:]


sock = socket.socket()  # создание сокета
average_port = 9090
while True:
    try:
        sock.bind(('', average_port))
        print("Используется порт: " + str(average_port))
        break
    except OSError as error:
        print("{} (порт {} занят)".format(error, average_port))
        average_port = random.randint(1024, 65535)

flag1, breaker, attempts = True, False, 3
while True:
    sock.listen(1)  # включаем режим прослушивания
    if flag1:
        logger("Включён режим прослушивания.")
        flag1 = not flag1
    conn, addr = sock.accept()  # получаем новый сокет и адрес клиента

    with open('clients.txt', 'a+') as clients_list:
        clients_list.seek(0, 0)
        #  поиск имеющегося клиента
        for line in clients_list:
            if addr[0] in line:
                logger("Подключение известного клиента: " + addr[0])
                sender(conn, 'known')
                sender(conn, "Здравствуйте, " + line[line.index('|') + 1:line.rindex('|')] + "!")
                while True:
                    sender(conn, "Введите свой пароль: ")
                    logger("Запрос пароля клиента: " + addr[0])
                    password = reciever(conn)
                    if line[line.rindex('|') + 1:] == hashlib.md5(password.encode()).hexdigest():
                        sender(conn, "true")
                        sender(conn, "Вы подтвердили свой пароль!")
                        logger("Клиент подтвердил свой пароль")
                        break
                    else:
                        attempts -= 1
                    if attempts == 0:
                        sender(conn, 'false')
                        sender(conn, "Количество попыток исчерпано!")
                        break
                break
        else:
            #  запись нового клиента с его паролем и именем
            sender(conn, 'new')  # флаг, означающий первое подключение клиента
            sender(conn, "Вы незарегистрированный пользователь! Введите ваше имя: ")  # 1 сообщение клиенту
            name = reciever(conn)  # 1 сообщение от клиента
            sender(conn, "Введите пароль: ")  # 2 сообщение клиенту
            password = reciever(conn)  # 2 сообщение от клиента
            password = hashlib.md5(password.encode()).hexdigest()  # хешерование пароля
            clients_list.write('\n' + addr[0] + '|' + name + '|' + password)
            logger("Запись нового клиента: " + addr[0])

    if attempts != 0:
        logger("Успешное соединение клиента: " + addr[0])

        while True:
            message = reciever(conn)  # читаем данные по 1 Кб и декадируем в текст
            if not message:
                logger("Отключение клиента: " + addr[0])
                break
            logger("Полученное сообщение: " + message)
            if message == 'shutdown':
                breaker = not breaker
                break
        if breaker:
            logger("Отключение сервера.")
            conn.close()  # закрываем соединение
            break

f.close()
