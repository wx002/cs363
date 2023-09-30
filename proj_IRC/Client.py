from socket import *
import re
import sys
import select
import threading
import curses


class IRC_Cient:
    COMMAND_LIST = ['/join', '/msg', '/part', '/quit', '/list', 'help', '/create', '/names']

    def __init__(self, server_ip, server_port, nick):
        self.IP = server_ip
        self.port = server_port
        self.name = nick
        self.skt = socket(AF_INET, SOCK_STREAM)
        self.skt.connect((self.IP, self.port))

    def register(self):
        # sending register nick
        register_str = b'NICK ' + self.name.encode()
        self.skt.sendall(register_str)

    def print_server_reply(self):
        try:
            while True:
                resp = '\n'+self.skt.recv(5000).decode() + '\n'
                if len(resp)>0:
                    print(resp)
                else:
                    continue
        except Exception as e:
            print(e)
            sys.exit()


    def is_valid_message(self, msg):
        msg_list = msg.split(' ')
        if msg_list[0] not in IRC_Cient.COMMAND_LIST and len(msg_list) < 3:
            return False
        else:
            return True

    def main(self):
        print('Simple IRC Client, CSCI 363 IRC Project\nMade by Ben Xu\nRun using Python 3.7.1\nUse /help for supported command list!')
        self.register()
        while True:
            user_input = input()
            if self.is_valid_message(user_input):
                self.skt.sendall(user_input.encode())
                if user_input == '/quit':
                    print('Good bye!')
                    sys.exit()
                elif user_input == 'help':
                    print('command list: /msg, /join, /part, /quit, /list, /create, /help. For details, do /help --detail')
                elif user_input == 'help --detail':
                    print('/msg : /msg [target] : [message] -- sends a message to a user or channel\n'
                          '/join: /join [channel] --  join a specific channel\n'
                          '/part: /part [channel] -- leave a channel\n'
                          '/quit: /quit -- log off\n'
                          '/names: /names -- display list of online users'
                          '/create: /create [channel name] -- create a channel with given name')

            else:
                print('Invalid message format')
                # TODO help function


if __name__ == '__main__':
    if len(sys.argv) == 4:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        nick = sys.argv[3]
        client = IRC_Cient(ip,port, nick)
    else:
        client = IRC_Cient('127.0.0.1', 6667, 'test')
    try:
        recv_thread = threading.Thread(target=client.print_server_reply)
        recv_thread.setDaemon(True)
        recv_thread.start()
        client.main()
    except Exception as e:
        print(e)
        sys.exit()
