
from chat_client_class import *

import copy

def main():
    import argparse
    parser = argparse.ArgumentParser(description='chat client argument')
    parser.add_argument('-d', type=str, default=None, help='server IP address')
    args = parser.parse_args()

    # client = Client(args)
    # client.run_chat()
    client = copy.GUI(args)
    client.run_chat()



main()
