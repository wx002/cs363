import select
import socket
import logging


class Channel:
    def __init__(self, name, server_ip):
        self.name = name
        self.server = server_ip
        self.ch_socket_list = {} #name:skt

    def broadcast(self, skt, msg):
        if skt in self.ch_socket_list.values():
            packet = msg.encode()
            for s in self.ch_socket_list.values():
                try:
                    s.sendall(packet)
                except:
                    continue
        else:
            skt.sendall('442 - {}:You\'re not on that channel'.format(self.name).encode())

    def welcome(self, name, user_skt):
        if name not in self.ch_socket_list:
            reply = name + '!'+name + '@'+ self.server + ' JOIN ' + self.name
            self.ch_socket_list[name] = user_skt
            self.broadcast(user_skt, reply)
            # send current list of user to socket
            user_list =','.join(self.ch_socket_list.keys())
            user_packet = ':{} 332\n{} {} :{}'.format(self.server, name, self.name, user_list)
            user_skt.sendall(user_packet.encode())
        else:
            user_skt.sendall('443 - {} is already in {}'.format(name, self.name).encode())

    def leave(self, name):
        if name in self.ch_socket_list:
            skt = self.ch_socket_list[name]
            self.broadcast(skt, '{}:{} has left the channel!'.format(self.name, name))
            del self.ch_socket_list[name]



















