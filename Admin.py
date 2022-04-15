import socket
import pickle
import threading
import math
from typing import Tuple, List

from Node import BUFFER_SIZE

class Admin:
    def __init__(self, ip: str, port: int) -> None:
        self.ip: str = ip
        self.port: int = port
        self.address: Tuple = (ip, port)
        self.nodes: List[Tuple] = []
        self.number_of_nodes: int = 1
        self.max_successors: int = math.ceil(math.log10(self.number_of_nodes))

        try:
            self.server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(self.address)
            self.server.listen()
        except socket.error:
            print("[__init__] - Error creating server.")

    def start(self) -> None:
        threading.Thread(target=self.__server_loop).start()

    def __server_loop(self) -> None:
        while True:
            try:
                print(f"[__server_loop] - Server is running at {self.address}")
                connection, address = self.server.accept()
                threading.Thread(target=self.__handle_connection, args=(connection, address)).start()
            except socket.error:
                print("[__server_loop] - Server could not accept client connection.")
            
    def __handle_connection(self, connection, address) -> None:
        print(f"[__handle_connection] - Establishing connection with {address}.")

        data = pickle.loads(connection.recv(BUFFER_SIZE))

        connection_type = data[0]

        if connection_type == 1:
            node_data = data[1]
            self.__send_prime_data(connection, node_data)
        if connection_type == 2:
            node_data = data[1]
            self.__delete_node(node_data)
        if connection_type == 3:
            admin_data = data[1]
            self.__dialog_admin(admin_data)

        connection.close()

    def __send_prime_data(self, connection, node_data: Tuple) -> None:
        if self.number_of_nodes > 1:
            index = len(self.nodes)
            successor_node = self.nodes[len(self.nodes) - 1]
            predecessor_node = self.nodes[len(self.nodes) - 2]

            data = pickle.dumps((index, successor_node, predecessor_node))
            connection.sendall(data)
            self.nodes.append((index, node_data))
        else:
            index = 0
            successor_node = None
            predecessor_node = None

            data = pickle.dumps((index, successor_node, predecessor_node))
            connection.sendall(data)
            self.nodes.append((index, node_data))

        self.number_of_nodes += 1

    def __delete_node(self, node_data: Tuple) -> None:
        pass

    def __dialog_admin(self, admin_data: Tuple) -> None:
        pass