import pickle
import socket
import time
from typing import Tuple, List
import threading

BUFFER_SIZE: int = 4096

class Node:
    def __init__(self, ip: str, port: int) -> None:
        self.id: int = None
        self.ip: str = ip
        self.port: int = port
        self.address: Tuple = (ip, port)
        self.table: List[Tuple] = []
        self.successor_nodes: List[Tuple] = []
        self.predecessor_node: Tuple = None

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(self.address)
            self.server.listen()
        except socket.error:
            print("[__init__] - Error creating server.")
    
    def start(self) -> None:
        # Get admin data
        self.__get_prime_data()

        # Start node connections
        threading.Thread(target=self.__server_loop).start()
        threading.Thread(target=self.__menu).start()

    def __get_prime_data(self) -> None:
        client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 5000))

        message = (1, self.address)
        print(f"[__get_prime_data] - Sending {message} to Admin.")
        data = pickle.dumps(message)
        client.sendall(data)

        prime_data = client.recv(BUFFER_SIZE)
        prime_message = pickle.loads(prime_data)

        index = prime_message[0] # TODO -> Create id with index

        if prime_message[1] != None and prime_message[2] != None:
            self.successor_nodes.append(prime_message[1])
            self.predecessor_node = prime_message[2]

            self.__establish_connection()

    def __establish_connection(self) -> None:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(self.successor_nodes[0][1])

        message = (4, 2, self.address)
        data = pickle.dumps(message)

        client.sendall(data)
        client.close()

        self.__ping_successors()

    def __ping_successors(self) -> None:
        for node in self.successor_nodes:
            threading.Thread(target=self.__ping_successor, args=(node[1])).start()

    def __ping_successor(self, address: Tuple) -> None:
        print(f"[__ping_successor] - PING {address}.")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(address)

        message: Tuple = (1)
        data = pickle.dumps(message)

        while True:
            client.sendall(data)
            message = pickle.loads(client.recv(BUFFER_SIZE))
            print(f"[__ping_successor] - {message} from {address}.")

            time.sleep(1)

    def __server_loop(self) -> None:
        while True:
            try:
                print(f"[__server_loop] - Node server is running on port {self.port}.")
                connection, address = self.server.accept()
                self.server.settimeout(120)

                threading.Thread(target=self.__handle_connection, args=(connection, address)).start()
            except socket.error:
                print("[__server_loop] - Error connecting to client.")

    def __handle_connection(self, connection, address: Tuple) -> None:
        print(f"[__handle_connection] - The node {address} is now connected!")

        data = pickle.loads(connection.recv(BUFFER_SIZE))
        connection_type = data[0]

        if connection_type == 1:
            # Ping - return pong
            print(f"[__handle_connection] - ping from {address}.")
            connection.sendall(pickle.dumps("pong"))
        elif connection_type == 2:
            # Receive data
            pass
        elif connection_type == 3:
            # Send data
            pass
        elif connection_type == 4:
            # Leave network - receive new successor or predecessor node
            if data[1] == 1:
                # Refresh sucessor node
                pass
            elif data[1] == 2:
                # Refresh predecessor
                new_address: Tuple = data[2]
                self.__refresh_predecessor(new_address)

    def __menu(self) -> None:
        while True:
            self.__print_menu()
            option = int(input("Type your option: "))

            if option == 1:
                # Send blockchain the successor(s) node(s)
                self.__send_blockchain()
            if option == 2:
                # Send block to successo(s) node(s)
                self.__send_block()
            if option == 3:
                # Receive block from predecessor node
                self.__ask_blockchain()
            if option == 4:
                # Show node details
                self.__print_node()
            if option == 5:
                # Show the successors nodes and the successor node
                self.__print_near_nodes()
            if option == 6:
                # Show your table with blockchain data
                self.__print_blockchain()
            if option == 7:
                # Leave network
                self.__leave_network()

    # BASIC FUNCTIONS
    def __refresh_predecessor(self, address) -> None:
        self.predecessor_node = address

    def __send_blockchain(self) -> None:
        pass
    
    def __send_block(self) -> None:
        pass

    def __ask_blockchain(self) -> None:
        # Ask for predecessor or successors nodes the blockchain
        pass
    
    def __print_node(self) -> None:
        data = f'''
            MY NODE:
             - ID: {self.id}
             - ADDRESS: {self.address}
        '''

        print(data)

    def __print_near_nodes(self) -> None:
        data = '''
            NEAR NODES:
             * SUCCESSOR(S) NODE(S):            
        '''
        print(data)

        for node in self.succ_nodes:
            temp_data = f'''
                  - Node #{node[0]} -> ({node[1]}, {node[2]})
            '''
            print(temp_data)

        print(f'''
             * PREDECESSOR NODE:
              - Node {self.pred[0]} -> ({self.pred[1]}, {self.pred[2]})
        ''')

    def __print_blockchain(self) -> None:
        pass

    def __leave_network(self) -> None:
        pass

    def __print_menu(self) -> None:
        data = '''
1 - Send block or blockchain
2 - Send block 
2 - Ask for block or blockchain
3 - Show node details
4 - Show network details
5 - Show blockchain details
6 - Leave network
        '''

        print(data)