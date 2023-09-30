import socket
import base64
import re
import linecache
import sys
import argparse

def PrintException():
    '''
       Print detail exception details
       taken from: https://stackoverflow.com/questions/14519177/python-exception-handling-line-number
       :return:
       '''
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

def chunk(line, size=1028):
    return [line[i:i+size] for i in range(0,len(line), size)]


def hash_string(string):
    str_hash =  base64.b64encode(string.encode()) + b'\t'
    return str_hash


def send_line(network, dest, line_bytes, size):
    if len(line_bytes) < size:
        # send the line directly if is less than the max size
        network.sendto(line_bytes, dest)
    else:
        lineChunks = chunk(line_bytes, size)
        for c in lineChunks:
            network.sendto(c, dest)

    network.sendto(b'####', dest)

def build_packet(index, line):
    hash_index = hash_string(str(index))
    hash_str = hash_string(line)
    hashed_line = hash_index + hash_str + line.encode()
    return hashed_line


def rdt_sendFile(network, dest, filename, size=65536):
    # generate lines from file
    file = open(filename)
    lines = file.readlines()  #will this work with binary files?
    line_count = len(lines)
    currentIndex = 0
    while currentIndex < line_count:
        ack = False
        while not ack:
            try:
                # build hash

                hashed_line = build_packet(currentIndex, lines[currentIndex])
                #print('index: {}\tLine:{}'.format(currentIndex,lines[currentIndex]))
                send_line(network, dest, hashed_line, size)
                print('sending packet index {}'.format(currentIndex))
                data = network.recv(size)

                #handle acks
                ackList = re.split('\t', data.decode(), maxsplit=1)
                index = int(base64.b64decode(ackList[1].encode()))
                print('Got ack for packet {} and currentIndex is {}'.format(index, currentIndex))
                if ackList[0] == 'ACK' and index == currentIndex:
                    ack = True
                    currentIndex += 1
                    print("acked! packet index is now {}".format(currentIndex))
                elif data == b'NNNN':
                    #current_line = build_packet(currentIndex, lines[currentIndex])
                    print('resending packet {},{}'.format(currentIndex, lines[currentIndex]))
                    send_line(network, dest, hashed_line, size)
            except KeyboardInterrupt:
                print('Ctrl-c, goodbye!')
                exit()
            except socket.timeout:
                print('timeout!')
            except:
                PrintException()

    END = False
    while not END:
        network.sendto(b'END', dest)
        data = network.recv(size)
        if data == b'END':
            END = True
    network.close()


def get_argus():
    '''
    gets the arguements
    :return:
    '''
    parser = argparse.ArgumentParser(
        description="Sender For RDT stop and wait with checksum"
    )
    parser.add_argument('--remote_addr',
                        default='127.0.0.1',
                        help='The remote address to send to.')
    parser.add_argument('--remote_port',
                        default=8880, type=int,
                        help='The remote address port')
    parser.add_argument('--file',
                        default='sendData/alice.txt',
                        help='The file to send')
    return parser.parse_args()


if __name__ == '__main__':
    argus = get_argus()
    ip = argus.remote_addr
    port = argus.remote_port
    dest = (ip, port)
    timeOut = 10
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeOut)
    file_name = 'alice.txt'
    filepath = 'sendData/'+file_name
    rdt_sendFile(sock, dest, filepath)
