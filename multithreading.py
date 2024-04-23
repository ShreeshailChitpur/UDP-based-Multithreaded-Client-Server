import socket
import time
import zlib
import ntpath
from struct import *


def receiver():
    def listen(fragments):      # Listens for fragments of data, validates them using a CRC check, and acknowledges the sender.
        # It continues listening until all fragments are received, and then reconstructs the original data.
        data_stream = []
        data_received = []
        for i in range(fragments):
            data_stream.append(b'')
            data_received.append(-1)

        while (-1 in data_received):
            received, client_address = server_socket.recvfrom(1032)
            header = received[:8]
            data = received[8:]
            msg_type, num, crc = unpack('bhL', header)
            if crc == zlib.crc32(data):
                reply = pack('bhL', 7, num, 0)
                data_stream[num] = data
                data_received[num] = 1
                print("*Fragment", num, "received correctly*")
            else:
                reply = pack('bhL', 8, num, 0)
                print("*Fragment", num, "received incorrectly*")
            server_socket.sendto(reply, client_address)

        final = b''
        for i in range(len(data_stream)):
            final = final + data_stream[i]

        return final

    server_port = int(input("Enter port number to listen on: "))

    server_ip = socket.gethostbyname(socket.gethostname())
    print("Your IP address is:", server_ip)

    spacer()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((server_ip, server_port))

    data, client_address = server_socket.recvfrom(1032)
    initiation = pack('bhL', 1, -1, 0)
    if data == initiation:
        server_socket.sendto(initiation, client_address)
        print("Connection established")
        spacer()

    while True:
        # Initialization of communication
        while True:
            data, client_address = server_socket.recvfrom(1032)
            msg_type, size, temp = unpack('bhL', data)
            if msg_type == 3 or msg_type == 4 or msg_type == 11:
                break

        if msg_type == 3:
            temp_data = listen(size)
            msg = temp_data.decode('utf-8')
            spacer()
            print(f"Received message from {client_address}: {msg}")
            spacer()

        elif msg_type == 4:
            temp_data = listen(size)
            filename = temp_data.decode('utf-8')

            data, client_address = server_socket.recvfrom(1032)
            msg_type, size, temp = unpack('bhL', data)

            file_data = listen(size)

            print(f"Path, where should be file {filename} saved?")
            path = input()
            with open(path + "\\" + filename, "wb") as out_file:
                out_file.write(file_data)

            print(f"File was saved to: {path}\\{filename}")
            spacer()

        elif msg_type == 11:
            termination = pack('bhL', 11, -1, 0)
            if data == termination:
                server_socket.sendto(termination, client_address)
            break

    server_socket.close()


def sender():
    def menu():
        print("Enter: 0 for terminating connection; 1 for sending text message; 2 for sending file")
        temp = int(input())
        spacer()
        return temp

    def initiate(client_address): #Attempts to establish a connection with a client. Retries if unsuccessful.
        c = 0
        client_socket.settimeout(0.5)
        while c < 5:
            c += 1
            try:
                data_send = pack('bhL', 1, -1, 0)
                client_socket.sendto(data_send, client_address)
                data_received, server_address = client_socket.recvfrom(1032)
                if data_send == data_received:
                    print("Connection established")
                    spacer()
                    client_socket.settimeout(None)
                    return 0
            except:
                print(
                    f"Connecting to {client_address} failed, trying again in {c} seconds.")
                time.sleep(c)
        print("Failed to establish connection, ending")
        client_socket.settimeout(None)
        return -1

    def send_msg(client_address):   #Takes user input for a text message and sends it to a specified client.
        msg = input("Enter message to send: ")
        msg = msg.encode('utf-8')

        print("Allow simulating faults during transmit? Enter: 1 for Yes; 2 for No")
        sim = int(input())

        send_data(msg, 5, sim, client_address)

    def send_file(client_address):                  # Takes a file path, reads the file, and sends it in fragments to a specified client.
        path = input("Enter filepath for file:")
        filename = ntpath.basename(path)
        filename = filename.encode('utf-8')

        print("Allow simulating faults during transmit? Enter: 1 for Yes; 2 for No")
        sim = int(input())

        # Simulating faults explicitly turned off to avoid confusion with doubling fragment numbers
        send_data(filename, 6, 2, client_address)

        # Sending file
        with open(path, "rb") as in_file:
            file_data = in_file.read()

        send_data(file_data, 6, sim, client_address)

    def end_conn(client_address):           # Attempts to terminate the connection with a client. Retries if unsuccessful.
        c = 0
        client_socket.settimeout(0.5)
        while c < 5:
            c += 1
            try:
                data_send = pack('bhL', 11, -1, 0)
                client_socket.sendto(data_send, client_address)
                data_received, server_address = client_socket.recvfrom(1032)
                if data_send == data_received:
                    print("Connection terminated")
                    spacer()
                    client_socket.settimeout(None)
                    return 0
            except:
                print(
                    f"Failed to terminate connection with {client_address}, trying again in {c} seconds")
                time.sleep(c)
        print("Failed to terminate connection, ending")
        print("----------------------------------------------------------------")
        client_socket.settimeout(None)
        return -1

    def send_data(data, msg_type, simulate_faults, client_address):             # Sends data in fragments to a specified client with error simulation options.
        data_stream = []
        data_confirmed = []

        if len(data) > max_size:
            for i in range(len(data) // max_size + 1):
                data_stream.append(data[i * max_size:(i + 1) * max_size])
                data_confirmed.append(-1)
        else:
            data_stream.append(data)
            data_confirmed.append(-1)

        # Initiation
        data_send = b''
        if msg_type == 5:
            data_send = pack('bhL', 3, len(data_stream), 0)
        if msg_type == 6:
            data_send = pack('bhL', 4, len(data_stream), 0)
        client_socket.sendto(data_send, client_address)

        client_socket.settimeout(0.2)
        while -1 in data_confirmed:
            for i in range(len(data_stream)):
                if data_confirmed[i] == -1:
                    data_send = pack('bhL', msg_type, i,
                                     zlib.crc32(data_stream[i]))

                    x = ""
                    if simulate_faults == 1:
                        print(
                            f"Simulate fault on fragment number {i}? Enter 1 for Yes; Press Enter for No")
                        x = input()
                    if x == "":
                        client_socket.sendto(
                            data_send + data_stream[i], client_address)
                    elif x == "1":
                        client_socket.sendto(
                            data_send + data_stream[i][:len(data_stream[i]) // 2], client_address)

                    try:
                        data_received, server_address = client_socket.recvfrom(
                            1032)
                        msg_type, num, crc = unpack('bhL', data_received)
                        if msg_type == 7:
                            data_confirmed[num] = 1
                        if msg_type == 8:
                            data_confirmed[num] = -1
                    except:
                        print(
                            f"Confirmation for fragment number {i} not received")

        client_socket.settimeout(None)

    server_ip = input("Enter receiver's IP address: ")

    while True:
        try:
            num_clients = int(input("Enter the number of clients: "))
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    client_addresses = []
    for i in range(num_clients):
        port = int(input(f"Enter port number for client {i + 1}: "))
        client_addresses.append((server_ip, port))

    max_size = int(input("Enter maximal fragment size (limited to 1024): "))

    spacer()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for address in client_addresses:
        if initiate(address) == -1:
            return

    selector = menu()

    while selector != 0:
        for address in client_addresses:
            if selector == 1:
                send_msg(address)
            elif selector == 2:
                send_file(address)
            spacer()
        selector = menu()

    for address in client_addresses:
        end_conn(address)


def spacer():
    print()
    print("----------------------------------------------------------------")
    print()


def main():
    while True:
        print("(sender / receiver / end)")
        temp = input("Select mode: ")
        spacer()
        if temp == "sender":
            sender()
        elif temp == "receiver":
            receiver()
        elif temp == "end":
            return 0
        else:
            print("Entered mode not found. Try again!")


if __name__ == '__main__':
    main()
