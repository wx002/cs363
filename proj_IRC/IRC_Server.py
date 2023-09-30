import socket
import select
import logging
import sys
from irc_db import *

class IRC_Server:
    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.server_name = name
        self.db = irc_db()
        self.log = logging.getLogger()

    def main(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.ip, self.port))
        server.listen()
        server.setblocking(False)

        self.db.create_channel('#Lobby', self.ip)
        self.log.info('Initalized #Lobby.....\nCurrent Channel List: {}'.format(list(self.db.channelList.keys())))
        self.log.info("Server running on {}".format((self.ip, self.port)))

        while True:
            try:
                r, w, e = select.select([server] + self.db.socket_list, [], self.db.socket_list, 1)
                #self.log.info('users: {}'.format(self.users))
                for skt in e:
                    self.log.info("Socket closed on {}".format(skt))
                    self.db.remove_by_skt(skt)

                if len(e) > 0:
                    continue

                for skt in r:
                    if skt  == server:
                        cli, cli_addr = skt.accept()
                        cli.setblocking(False)
                        # got client
                        self.db.init_user(cli)
                    else:
                        try:
                            msg = skt.recv(5000)
                        except ConnectionResetError:
                            msg = ''
                        if len(msg) > 0:
                            self.log.info('packet recv from {}, content: {}'.format(skt.getpeername(), msg))
                            self.log.info('Current user in db : {}'.format(self.db.users.keys()))
                            if not self.db.is_in_db_by_skt(skt):
                                # expect NICK packet
                                resp_code = self.auth(msg, skt)
                                self.log.info('auth resp: {}'.format(resp_code))
                                if resp_code == -1:
                                    self.db.remove_by_skt(skt)
                                    skt.close()
                                else:
                                    continue
                            else:
                                # handle msg packet
                                cmd, target, content = self.parse_packet(msg)
                                self.log.info('recv msg packet! cmd = {}, target = {}, content = {}'.format(cmd, target, content))
                                if cmd == '/msg' and target is not None and content is not None:
                                    if '#' in target and target in self.db.channelList:
                                        sender_ip = skt.getpeername()[0]
                                        name = self.db.users[skt]
                                        header = self.build_packet_header(name, sender_ip)
                                        sending_packet = header + ' ' + msg.decode()
                                        self.db.channelList[target].broadcast(skt, sending_packet)
                                        self.log.info('Broadcasting: {}'.format(sending_packet))
                                    elif '#' not in target and content is not None:
                                        # send to users,
                                        if target in self.db.users:
                                            name = self.db.users[skt]
                                            sender_ip = skt.getpeername()[0]
                                            header = self.build_packet_header(name, sender_ip)
                                            sending_packet = header + ' ' + msg.decode()
                                            self.db.users[target].sendall(sending_packet.encode())
                                        else:
                                            skt.sendall('444 {}:User not logged in!'.format(target).encode())
                                    else:
                                        p = '461 {} not enough or invalid parameters'.format(cmd)
                                        skt.sendall(p.encode())
                                elif cmd == '/join' and target is not None:
                                    if target in self.db.channelList:
                                        if skt not in self.db.channelList[target].ch_socket_list and skt in self.db.users:
                                            name = self.db.users[skt]
                                            self.db.channelList[target].welcome(name, skt)
                                        else:
                                            p = '443 - Already in channel'
                                            skt.sendall(p.encode())
                                    else:
                                        skt.sendall('ERROR - Channel {} does not exists'.format(target).encode())
                                elif cmd == '/part' and target is not None:
                                    name = self.db.users[skt]
                                    if target in self.db.channelList:
                                        if name in self.db.channelList[target].ch_socket_list:
                                            self.db.channelList[target].leave(name)
                                        else:
                                            skt.sendall('442 - {}:You\'re not in that channel'.format(name).encode())
                                    else:
                                        skt.sendall(b'Channel does not exists!')
                                elif cmd == '/quit':
                                    self.db.remove_by_skt(skt)
                                    skt.close()
                                elif cmd == '/list':
                                    skt.sendall('332 - Channels: {}'.format(','.join(self.db.channelList.keys())).encode())
                                elif cmd == '/create' and target is not None:
                                    if target not in self.db.channelList:
                                        name = self.db.users[skt]
                                        self.db.create_channel(target, self.ip)
                                        self.db.channelList[target].welcome(name, skt)
                                    else:
                                        skt.sendall('Error - channel {} already exists'.format(target).encode())
                                elif cmd == '/names':
                                    names = [elm for elm in self.db.users.keys() if isinstance(elm, str)]
                                    nameList = ','.join(names)
                                    p = 'Online Users: {}'.format(nameList)
                                    skt.sendall(p.encode())
                                else:
                                    skt.sendall(b'Error - unknown packet!')
                        else:
                            try:
                                self.log.debug("disconnect from {}".format(skt.getpeername()))
                                self.db.remove_by_skt(skt)
                                skt.close()
                            except:
                                pass
            except KeyboardInterrupt:
                print("Ctrl-c, quit!")
                break

    def auth(self, packet, skt):
        msg = packet.decode()
        if 'NICK' in msg:
            msgList = msg.split(' ')
            name  = msgList[1]
            if self.db.register_user(name, skt):
                RPL_WELCOME = ':{} 001 {} Welcome to the {}!{}@{}'.format(self.ip, name, self.server_name, name,name,skt.getpeername()[0])
                skt.sendall(RPL_WELCOME.encode())
                # join #Lobby
                self.db.channelList['#Lobby'].welcome(name, skt)
                return 1
            else:
                skt.sendall(b'433 - Nickname already in use')
                return -1
        else:
            return 0

    def parse_packet(self, packet):
        #cmd target :msg
        if b':' in packet:
            msgList = packet.decode().split(':')
            prefix = ''.join(msgList[0]).split(' ')
            cmd = prefix[0]
            target = prefix[1]
            content = msgList[1]
            return cmd, target, content
        else:
            # server commands
            cmd_str = packet.decode()
            cmd_list = cmd_str.split(' ')
            if len(cmd_list) == 2:
                return  cmd_list[0], cmd_list[1], None
            elif len(cmd_list) == 1:
                return cmd_list[0], None, None
            else:
                return None, None, None

    def build_packet_header(self,name, sender_ip):
        header = ':{}!{}@{}'.format(name, name, sender_ip)
        return header




if __name__ == '__main__':
    if len(sys.argv) == 4:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        name = sys.argv[3]
    else:
        print('--usage: Python IRC_Server [ip] [port] [server name]')


    debug = True
    if debug:
        FORMAT = '%(asctime)-15s %(levelname)-6s: %(message)s'
        logging.basicConfig(filename='server.log', format=FORMAT, level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    server = IRC_Server(ip, port, name)
    server.main()
