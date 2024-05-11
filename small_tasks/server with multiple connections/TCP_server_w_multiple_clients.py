import selectors
import socket
import random
import time


sel = selectors.DefaultSelector()


def generate_random_number() -> int:
    return random.randint(1, 1000)


def accept(sock: socket.socket, mask) -> None:
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)

    # Добвляем клиента в список клиентов
    sel.register(conn, selectors.EVENT_READ, read)


def read(conn, event) -> None:
    data = conn.recv(1024)
    if data:
        time.sleep(1)
        random_number = generate_random_number()
        print(f"Sending {random_number} to {conn}")
        conn.sendall(str(f"{random_number}\n\r").encode())
    else:
        print(f"Closing connection with {conn}")
        sel.unregister(conn)
        conn.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Это позволяет повторно использовать адрес и порт
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("192.168.1.40", 23))
    server_socket.listen()

    # Устанавливаем серверный сокет в неблокирующий режим
    server_socket.setblocking(False)

    # Регистируем серверный сокет в селекторе для чтения
    sel.register(server_socket, selectors.EVENT_READ, accept)
    print("Server started")

    while True:
        try:
            events = sel.select()
            for key, event in events:
                callback = key.data
                callback(key.fileobj, event)
        except KeyboardInterrupt:
            print("Server stopped")
            break


if __name__ == "__main__":
    main()
