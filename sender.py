import socket
import argparse
import struct
import datetime
import time
import sys

# Packet types
REQUEST_PACKET = b'R'
DATA_PACKET = b'D'
END_PACKET = b'E'

# Header format
HEADER_FORMAT = '!cII'


def send_end_packet(seq_num, ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_type = END_PACKET
    length = 0
    header = struct.pack(HEADER_FORMAT, packet_type, seq_num, length)
    packet = header
    sock.sendto(packet, (ip, port))
    print("END Packet")
    print("send time:        ", datetime.datetime.now())
    print("requester addr:   ", ip, ":", port)
    print("sequence num:     ", seq_num)
    print("length:           ", length)
    print("payload:          ", )
    print("\n")


# Command line parameter
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--listen", type=int,
                    help="port on which the sender waits for requests")
parser.add_argument("-g", "--send_to", type=int,
                    help="requester port: port on which the requester is waiting")
parser.add_argument("-r", "--rate", type=int,
                    help="rate: the number of packets to be sent per second")
parser.add_argument("-q", "--seq_no", type=int,
                    help="seq_no: The initial sequence of the packet exchange")
parser.add_argument("-l", "--length", type=int,
                    help="length: the length of the payload(in bytes) in the packets")
args = parser.parse_args()

# Limitation of command line parameter
if not (2049 < args.listen < 65536):
    print("Error: Port number should be in the range of 2049 to 65536")
    sys.exit(1)
if not (2049 < args.send_to < 65536):
    print("Error: Requester port number should be in the range of 2049 to 65536")
    sys.exit(1)


# specify the IP address and port number of the receiver
requester_ip = '127.0.0.1'
sendto_port = args.send_to
listen_this_port = args.listen
send_rate = args.rate
payload_length = args.length
seq_num = args.seq_no
rate = args.rate

# create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((requester_ip, listen_this_port))
# print("sender is listening this port: ", listen_this_port, "\n")

# receive packets
while True:
    packet, addr = sock.recvfrom(1024)
    requester_ip = addr[0]
    udp_header = packet[:9]
    filename = packet[9:]

    # read the file to send
    try:
        with open(filename, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        send_end_packet()

    # split the data into packets
    packet_size = args.length
    packets = [data[i:i + packet_size] for i in range(0, len(data), packet_size)]

    # send each packet to the receiver
    for i, packet in enumerate(packets):
        packet_type = DATA_PACKET
        length = len(packet)
        payload = packet
        header = struct.pack(HEADER_FORMAT, packet_type, seq_num, length)
        packet = header + payload
        sock.sendto(packet, (requester_ip, sendto_port))
        print("DATA Packet")
        print("send time:        ", datetime.datetime.now())
        print("requester addr:   ", requester_ip, ":", sendto_port)
        print("sequence num:     ", seq_num)
        print("length:           ", length)
        print("payload:          ", payload.decode()[:4])
        print("\n")
        seq_num = seq_num + length
        time.sleep(1 / rate)
    send_end_packet(seq_num, requester_ip, sendto_port)
    sys.exit()
