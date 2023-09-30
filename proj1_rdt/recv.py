from socket import *
import re
import base64
import linecache
import sys
from datetime import datetime
import argparse


def get_argus():
    '''
    gets the arguements
    :return:
    '''
    parser = argparse.ArgumentParser(
        description="Receiver For RDT stop and wait with checksum"
    )
    parser.add_argument('--addr',
                        default='127.0.0.1',
                        help='The address of the sender to listen to')
    parser.add_argument('--port',
                        default=8888, type=int,
                        help='The port of the sender to listen to')
    return parser.parse_args()

argus = get_argus()
addr = argus.addr
port = argus.port
dest = (addr, port)
currentIndex = -1
sock = socket(AF_INET, SOCK_DGRAM)

sock.bind(dest)

fileList = []
lineStr = ''


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




def get_decode_list(byteString):
    # print("byteString: {}\tType: {}".format(byteString, type(byteString)))
    # string = byteString.decode('utf-8')
    stringList = re.split('\t', byteString, maxsplit=2)
    return stringList


def verify_packet_content(stringList):
    '''
    index 0: header index
    index 1: content hashed form in base64
    index 2: actual data
    '''
    try:
        if stringList[1] != None and stringList[2] != None:
            encoded_str = base64.b64decode(bytes(stringList[1], 'utf-8')).decode('utf-8')
            if encoded_str == stringList[2]:
                return True
        else:
            return False

    except Exception:
        return False


startTime = datetime.now()

print('established connection with server, waiting to receive...')
while True:
    data, addr = sock.recvfrom(1048)  # why 1048? what if a line is longer than 1048 bytes?

    #print("recv data: {}".format(data))
    while data != b'####' and data != b'END':
        try:
            lineStr += data.decode('utf-8')
        except Exception:
            # bad packet ask for resend
            sock.sendto(b'NNNN', addr)
        # print(get_decode_list(lineStr))
        data, addr = sock.recvfrom(1048)

    if data == b'####':
        #print('Got line end!')
        packetList = get_decode_list(lineStr)
        try:
            index = int(base64.b64decode(packetList[0].encode()))
            print('Got packet index {}\t Expecting packet index {}'.format(index, currentIndex+1))
            if index == currentIndex + 1:
                print('index match, verfying packet!')
                # verify content
                # print(verify_packet_content(packetList))
                if verify_packet_content(packetList):
                    fileList.append(packetList[2])
                    # update currentIndex
                    currentIndex += 1
                    print("Got packet! Recv Index: {}\tNext index: {}\tCurrentLine: {}".format(index, currentIndex+1,
                                                                                               packetList[2]))
                    print('sending ACK...')
                    sock.sendto(b'ACK\t'+ base64.b64encode(str(index).encode()), addr)

                    # print('recvived 1 line!')
                else:
                    # corrupted content, ask for the same line again
                    print('packet {} is corrupted, ask for line again!'.format(index))
                    sock.sendto(b'NNNN', addr)
            elif index == currentIndex and len(packetList) == 3:  # duplicated packet, resend ack
                print('resending ACK for packet index {}, next packet index is {}'.format(index, currentIndex+1))
                sock.sendto(b'ACK\t'+base64.b64encode(str(currentIndex).encode()), addr)
            else:
                print('packet error for index {} and current index {}! Ask for resend!',
                      format(str(index), str(currentIndex)))
                sock.sendto(b'NNNN', addr)
            lineStr = ''
        except:
            print(index, packetList)
            PrintException()
        # print(fileList)
        #lineStr = ''
        # data = ''
        #print(fileList)



    if data == b'END':
        print("got all contents!")
        sock.sendto(b'END', addr)
        sock.close()
        # make file
        file = open('recvData/recv.txt', 'w+')
        file.writelines(fileList)
        file.close()
        endTime = datetime.now()
        # print total time in sec
        total_time = (endTime-startTime).total_seconds()
        print('total time: {}'.format(total_time))
        file_size = 167546
        print('Transfer rate: {} bytes per second'.format(file_size/total_time))
        exit(0)
