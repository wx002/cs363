This is implementation of RDT (Reliable Data Transfer) protocol over UDP.  
  
Running instructions:  
0. Run udp_box.py with respective commandline arguments. addr=127.0.0.1, port=8880, remote_port=8888  
1. Run recv.py. Parameters: --addr (the address to listen to, default=127.0.0.1), --port (the port to listen to, default=8888)  
2. run sender.py. Parameters: --remote_addr(the remote address to send file to, default=127.0.0.1), --remote_port (the remote port to send file to, default=8880), --file (the file that will be sending, default=sendData/alice.txt)  

Note:  
    -SendData: File to send should be located in here  
    -recvData: The file received will be located here, named recv.txt  
The default configuration is meant to run with the udp_box, in the following configuration:  
sender.py <-> udp_box.py <-> recv.py  
  
Basic benchmark using udp_box:  
    conditions:  
        - 50kbs bandwidth  
        - Sending file: Alice.txt, size=167546 bytes  
        - parameters: loss rate, out of order rate(ooo_rate), duplicate packet rate(dupe_rate), byte error rate(ber)  
    Tested with 4 conditions (Ideal, good, medium, and terrible)  

Ideal: (--loss_rate 0 --ooo_rate 0 --dupe_rate 0 --ber 0)  
    - time:             118.819721s  
    - transfer rate:    1410.0857887050586 bytes per second  
  
Good: (--loss_rate 0.01 --ooo_rate 0.01 --dupe_rate 0.01 --ber 1e-8)  
    - time:             1239.808353s  
    - transfer rate:    135.1386281553791 bytes per second  
  
Medium: (--loss_rate 0.02 --ooo_rate 0.02 --dupe_rate 0.02 --ber 1e-6):  
    - time:             2393.281579s  
    - transfer rate:    70.00680633241944 bytes per second  
  
Terrible: (--loss_rate 0.1 --ooo_rate 0.03 --dupe_rate 0.05 --ber 1e-3):  
    - time:             Infinity  
    - transfer rate:    SLOW  
  
Pros:  
    - Ensures data is correctly transferee  
    - There is almost no chance of data error  
    - Packets arrive in sequential order  
    - Very reliable when the connection is decent, performs well within reasonable amount of time  
    - Will be able to run and sustain even under terrible conditions, with almost no data error  
Cons:  
    - It is not using the maximum bandwidth at all  
    - Transfer rate is very low since is sending lines  
    - It require insane amount of time with non ideal conditions  
    - Under terrible conditions, the transfer will last indefinitely  
    - Not taking advantage of the full bandwidth  

Possible additions:  
    - Add initial handshakes for the receiver to know what to name the file  
    - Add timeout phase to break out indefinite run times with terrible connection  
    - Consider revamping the algorithm to use more bandwidth  
Protocol sequence diagram:  
  
Sender                                  Receiver  
  | ---------------line 0------------------> |  
  | <--------------ACK for line 0----------- |  
  | ---------------line 1------------------> |  
  | <--------------ACK for line 1----------- |  
  | ---------------line 2------------------> |  
  | <--------------ACK for line 2----------- |  
  | ---------------line 3------------------> |  
  | <--------------ACK for line 3----------- |  
  | ---------------line 4------------------> |  
  | <--------------ACK for line 4----------- |  
  | ---------------line 4------------------> |  
  | <--------------ACK for line 4----------- |  
  | ---------------line 5------------------> |  
  | <--------------ACK for line 5----------- |  
  | ---------------line 6------------------> |  
  | <--------------ACK for line 6----------- |  
  | ---------------line 7------------------> |  
  | <--------------ACK for line 7----------- |  
  | ---------------line 8------------------> |  
  | <--------------ACK for line 8----------- |  
  | ---------------END   ------------------> |  
  | <--------------END---------------------- |  
Sender                                    Receiver  
  
Packet structure:  
Each packet is representing a line of the file. Header is the index. All packets arrive at sequential order.  
  
    structure: encoded Header + \t + encoded string + \t + raw data string  
  
Encoded Header:  
    - Index of the packet, encoded using base64  

Encoded String:  
    - The content of the line, encoded using base64

Verify Method:
    - Header must arrive in order, discard packet if is out of order and wait for resend  
    - The decoded encoded string must match the raw data string. Otherwise, packet is corrupted and ask for resend  

