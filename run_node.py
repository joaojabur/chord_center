from Node import Node
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-p", metavar="PORT", type=int, help="Port the node server runs at.")

    args = parser.parse_args()

    node = Node('127.0.0.1', args.p)
    node.start()