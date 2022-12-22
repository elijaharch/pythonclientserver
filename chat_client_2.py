import socket
import threading

def listen(s: socket.socket):
    while True:
        message = s.recv(1024)
        print('\r\r' + message.decode() + '\n' + 'you: ', end='')


def connect(host: str = '127.0.0.1', port: int = 9090):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s.connect((host, port))

    threading.Thread(target=listen, args=(s,), daemon=True).start()

    s.send('__join'.encode())

    while True:
        message = input('you: ')
        s.send(message.encode())

connect()