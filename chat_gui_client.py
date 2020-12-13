import GUI

def main():
    import argparse
    parser = argparse.ArgumentParser(description='chat client argument')
    parser.add_argument('-d', type=str, default=None, help='server IP address')
    args = parser.parse_args()

    client = GUI.GUI(args)
    client.run_chat()

main()
