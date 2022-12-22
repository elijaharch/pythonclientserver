import socket

def listen(host: str = '127.0.0.1', port: int = 9090):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    members = []

    s.bind((host, port))
    while True:
        message, address = s.recvfrom(1024)

        if address not in members:
            members.append(address)

        if not message:
            continue

        client_id = address[1]
        if message.decode() == '__join':
            print(f'Клиент {client_id} присоединился')
            continue

        message = f'Клиент {client_id}: {message.decode()}'
        for member in members:
            if member == address:
                continue
            s.sendto(message.encode(), member)

listen()