from Channel import *
class irc_db:
    def __init__(self):
        self.users = {} # name: socket and socket:name
        self.channelList = {} # channelName : Channel Object
        self.socket_list = [] # list of sockets

    def is_in_db(self, name):
        if name in self.users:
            return True
        else:
            return False

    def is_in_db_by_skt(self, skt):
        if skt in self.users:
            return True
        else:
            return  False

    def get_socket_by_name(self, name):
        if self.is_in_db(name):
            return self.users[name]

    def remove_by_name(self, name):
        if self.is_in_db(name):
            skt = self.users[name]
            del self.users[name]
            if skt in self.users:
                del self.users[skt]
            if skt in self.socket_list:
                self.socket_list.remove(skt)
            for c in self.channelList:
                if name in self.channelList[c].ch_socket_list:
                    self.channelList[c].leave(name)

    def remove_by_skt(self, skt):
        name = self.users[skt]
        if skt in self.users:
            del self.users[skt]
            if name in self.users:
                del self.users[name]

        if skt in self.socket_list:
            self.socket_list.remove(skt)

        for c in self.channelList:
            if name in self.channelList[c].ch_socket_list:
                self.channelList[c].leave(name)

    def register_user(self, name, skt):
        if not self.is_in_db(name) and skt not in self.users:
            self.users[name] = skt
            self.users[skt] = name
            return True
        else:
            return False

    def create_channel(self, ch_name, ip):
        if ch_name not in self.channelList and '#' in ch_name:
            self.channelList[ch_name] = Channel(ch_name, ip)


    def init_user(self, skt):
        if skt not in self.socket_list:
            self.socket_list.append(skt)


